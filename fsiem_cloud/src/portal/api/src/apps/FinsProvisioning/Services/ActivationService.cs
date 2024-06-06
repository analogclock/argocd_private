using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Threading.Tasks;
using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.DocumentModel;
using Amazon.DynamoDBv2.Model;
using FinsProvisioning.AwsExtensions;
using FinsProvisioning.Extensions;
using FinsProvisioning.Helpers;
using FinsProvisioning.Models;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace FinsProvisioning.Services
{
  public interface IActivationService
  {
    Task<bool> CreateAsync(Activate activate);
    Task<bool> UpdateAsync(Activate current, ActivatedStackInformation update);
    Task<Activate> GetAsync(string serialNumber);
    Task<bool> UpdateStatusAsync(string key, ActivateStatus status);
  }

  public class ActivationService : BaseService<Activate>, IActivationService
  {
    private readonly IDomainCertificateStore _domainCertificateStore;

    public ActivationService(IAmazonDynamoDB client,
      IDomainCertificateStore domainCertificateStore,
      IConfiguration config,
      ILogger<Activate> logger
    ) : base(client, config["DynamoDbTable"], logger)
    {
      _domainCertificateStore = domainCertificateStore ?? throw new ArgumentNullException(nameof(domainCertificateStore), "Domain store is null");
    }

    public async Task<bool> CreateAsync(Activate activate)
    {
      var doc = activate.ToDocument();
      Logger.LogInformation($"Inserting object into DynamoDB: {activate.ToJsonString()}");
      var request = new PutItemRequest(TableName, doc.ToAttributeMap());
      var put = await Client.PutItemAsync(request);

      // we have failed to put item into the database
      if (put.HttpStatusCode != HttpStatusCode.OK)
      {
        Logger.LogError($"Unable to add item to table {TableName}");
        Logger.LogError($"Offending JSON: {activate.ToJsonString()}");
        return false;
      }
      else
      {
        Logger.LogInformation($"Object inserted into DynamoDB OK");
      }

      return true;
    }

    public async Task<Activate> GetAsync(string serialNumber)
    {
      Logger.LogInformation($"Getting item with serial number: {serialNumber}");
      var response = await Client.GetBySerialNumberAsync(TableName, serialNumber);
      if (!response.IsItemSet)
      {
        Logger.LogError($"Unable to find item with serial number: {serialNumber}");
        return null;
      }

      Logger.LogInformation($"Item found with serial number: {serialNumber}");
      var doc = Document.FromAttributeMap(response.Item);
      return doc.ToJson().DeserializeCamel<Activate>();
    }

    public async Task<bool> UpdateAsync(Activate current, ActivatedStackInformation update)
    {
      Logger.LogInformation($"Updating deployment: {current.SerialNumber}");
      var changes = new Dictionary<string, AttributeValueUpdate>();
      if (update.ShouldUpdateSKU)
      {
        // we only want to update the SKU we have
        current.DeploymentSKU = update.DeploymentSKU;
        changes["deploymentSKU"] = update.DeploymentSKU.ToChange();
        // force license to be replayed
        changes.AddChange("licenseInsertedOn", "");
      }
      else
      {
        // we are updating all other fields
        if (update.Ipv4CIDRList != null)
        {
          Logger.LogInformation($"Updating ipV4 {current.IPV4Cidr} -> {update.Ipv4CIDRList}");
          current.IPV4Cidr = update.Ipv4CIDRList;
          changes.AddChange("ipV4Cidr", update.Ipv4CIDRList);
        }

        if (update.Ipv6CIDRList != null)
        {
          Logger.LogInformation($"Updating ipV6 -> {update.Ipv6CIDRList}");
          current.IPV6Cidr = update.Ipv6CIDRList;
          changes.AddChange("ipV6Cidr", update.Ipv6CIDRList);
        }

        if (update.AdditionalContacts != null)
        {
          Logger.LogInformation($"Updating additionalContacts -> {update.AdditionalContacts}");
          current.AdditionalContacts = update.AdditionalContacts;
          changes.AddChange("additionalContacts", update.AdditionalContacts);
        }

        if (update.ExternalStorageDest != null)
        {
          Logger.LogInformation($"Updating externalStorageDest -> {update.ExternalStorageDest}");
          current.ExternalStorageDest = update.ExternalStorageDest;
          changes.AddChange("externalStorageDest", update.ExternalStorageDest);
        }

        if (update.AlternateDomain != null)
        {
          if (string.IsNullOrWhiteSpace(update.AlternateDomain))
          {
            // we are actually just checking if the string is empty, or
            // just whitespace as we know its not null
            // we want to explicitly remove the certificate ARN in this case
            Logger.LogInformation($"Removing alternateDomain");
            current.AlternateCertificateARN = null;
            changes.AddChange("alternateCertificateARN", "");
          }

          Logger.LogInformation($"Updating alternateDomain -> {update.AlternateDomain}");
          current.AlternateDomain = update.AlternateDomain;
          changes.AddChange("alternateDomain", update.AlternateDomain);
        }

        if (update.Certificate != null)
        {
          Logger.LogInformation($"Updating certificate -> {update.Certificate.Body}");
          // we want to store the new certificate information
          var certificateARN = await _domainCertificateStore
            .With(current.SerialNumber, current.Endpoint)
            .SaveAsync(update.Certificate, current.AlternateCertificateARN);

          if (string.IsNullOrWhiteSpace(certificateARN))
          {
            Logger.LogError($"Unable to add alternate domain certificates: {current.SerialNumber}");
            return false;
          }

          current.AlternateCertificateARN = certificateARN;
          changes.AddChange("alternateCertificateARN", certificateARN);
        }
      }

      if (!changes.Any())
      {
        Logger.LogError("No update required, as no changes are available.");
        return false;
      }

      current.Status = ActivateStatus.UpdateInProgress;
      changes.AddChange("status", ActivateStatus.UpdateInProgress.ToString());

      var req = new UpdateItemRequest()
      {
        TableName = TableName,
        Key = GetSnKey(current.SerialNumber),
        AttributeUpdates = changes
      };

      var response = await Client.UpdateItemAsync(req);

      if (response.HttpStatusCode != HttpStatusCode.OK)
      {
        // update has failed, log an error and JSON for debug
        Logger.LogError($"Unable to update item to table {TableName}");
        Logger.LogError($"Offending JSON: {current.ToJsonString()}");

        // tell the rest that we've failed
        return false;
      }

      return true;
    }

    public async Task<bool> UpdateStatusAsync(string key, ActivateStatus status)
    {
      Logger.LogInformation($"Update status deployment: {key}");

      // update status to DeleteInProgress
      var update = await UpdateRow(key, status);

      // we have failed to update the item in the database
      if (update.HttpStatusCode != HttpStatusCode.OK)
      {
        Logger.LogError($"Unable to update status in table {TableName}");
        Logger.LogError($"Offending key: {key}");
        return false;
      }

      return true;
    }

    private static Dictionary<string, AttributeValue> GetSnKey(string key)
    {
      return new Dictionary<string, AttributeValue>
        {
          {"serialNumber", new AttributeValue(key)}
        };
    }

    private Task<UpdateItemResponse> UpdateRow(string serialNumber, ActivateStatus status)
    {
      var request = new UpdateItemRequest(TableName, GetSnKey(serialNumber), new Dictionary<string, AttributeValueUpdate>()
        {
          {
            "status", new AttributeValueUpdate(new AttributeValue(status.ToString()), AttributeAction.PUT)
          }
        });

      // update the status on the table row
      return Client.UpdateItemAsync(request);
    }
  }
}

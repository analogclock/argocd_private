using System.Collections.Generic;
using System.Threading.Tasks;
using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.Model;
using FinsProvisioning.AwsExtensions;
using FinsProvisioning.Extensions;
using FinsProvisioning.Models;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace FinsProvisioning.Services
{
  public interface IExternalStorageService
  {
    Task<List<ExternalStorage>> Get(string serialNumber);
    Task<bool> SaveAsync(ExternalStorage storage);
    Task<bool> DeleteAsync(ExternalStorage storage);
  }

  public class ExternalStorageService : BaseService<ExternalStorageService>, IExternalStorageService
  {
    public ExternalStorageService(
      IAmazonDynamoDB client,
      IConfiguration config,
      ILogger<ExternalStorageService> logger
      ) : base(client, config["ExternalStorageDynamoDbTable"], logger)
    { }

    public async Task<List<ExternalStorage>> Get(string serialNumber)
    {
      Logger.LogInformation("Getting external storage by its serial number: {}", serialNumber);
      return await Client.GetAllBySerialNumber<ExternalStorage>(TableName, serialNumber);
    }

    public async Task<bool> SaveAsync(ExternalStorage storage)
    {
      Logger.LogInformation($"Saving storage for {storage.SerialNumber}");
      var changes = new Dictionary<string, AttributeValueUpdate>();
      changes.AddChange("externalStorageDest", storage.ExternalStorageDest);
      var request = new UpdateItemRequest()
      {
        TableName = TableName,
        Key = new()
          {
              { "serialNumber", new AttributeValue(storage.SerialNumber) },
              { "organizationId", new AttributeValue() {N = storage.OrganizationId.ToString()} }
          },
        AttributeUpdates = changes
      };

      // updates perform an insert if it doesn't exist
      var response = await Client.UpdateItemAsync(request);

      if (response.HttpStatusCode == System.Net.HttpStatusCode.OK)
      {
        Logger.LogInformation("Saved external storage");
        return true;
      }

      Logger.LogError("Unable to store schedule");
      Logger.LogError($"Offending JSON: {storage.SerializeCamel()}");

      return false;
    }

    public async Task<bool> DeleteAsync(ExternalStorage storage)
    {
      var request = new DeleteItemRequest()
      {
        TableName = TableName,
        Key = new()
          {
              { "serialNumber", new AttributeValue(storage.SerialNumber) },
              { "organizationId", new AttributeValue() {N = storage.OrganizationId.ToString()} }
          }
      };

      // deletes where the item exists
      var response = await Client.DeleteItemAsync(request);

      if (response.HttpStatusCode == System.Net.HttpStatusCode.OK)
      {
        Logger.LogInformation("Deleted external storage");
        return true;
      }

      Logger.LogError("Unable to delete external storage");
      Logger.LogError($"Offending JSON: {storage.SerializeCamel()}");

      return false;
    }
  }
}

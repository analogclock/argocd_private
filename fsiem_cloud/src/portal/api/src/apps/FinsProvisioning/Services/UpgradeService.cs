using System.Collections.Generic;
using System.Threading.Tasks;
using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.DocumentModel;
using Amazon.DynamoDBv2.Model;
using FinsProvisioning.Extensions;
using FinsProvisioning.Models;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace FinsProvisioning.Services
{
  public interface IScheduledUpgradeService
  {
    Task<List<UpgradeModel>> GetAsync(string serialNumber);
    Task<bool> SaveAsync(UpgradeModel upgrade);
  }

  public class ScheduledUpgradeService : BaseService<ScheduledUpgradeService>, IScheduledUpgradeService
  {
    public ScheduledUpgradeService(
      IAmazonDynamoDB client,
      IConfiguration config,
      ILogger<ScheduledUpgradeService> logger
      ) : base(client, config["ScheduledUpgradeDynamoDbTable"], logger)
    { }

    public async Task<List<UpgradeModel>> GetAsync(string serialNumber)
    {
      Logger.LogInformation($"Getting scheduled upgrades for : {serialNumber}");

      var request = new QueryRequest()
      {
        TableName = TableName,
        KeyConditionExpression = "serialNumber = :serialNumber",
        ExpressionAttributeValues = new() { { ":serialNumber", new AttributeValue(serialNumber) } }
      };

      QueryResponse response;
      var updates = new List<UpgradeModel>();
      do
      {
        response = await Client.QueryAsync(request);
        foreach (var item in response.Items)
        {
          var doc = Document.FromAttributeMap(item);
          var mod = doc.ToJson().DeserializeCamel<UpgradeModel>();
          updates.Add(mod);
        }
      } while (response.LastEvaluatedKey.Count > 0);

      return updates;
    }

    public async Task<bool> SaveAsync(UpgradeModel upgrade)
    {
      Logger.LogInformation($"Saving schedule for {upgrade.SerialNumber}");
      var changes = new Dictionary<string, AttributeValueUpdate>();
      changes.AddChange("scheduledLocal", upgrade.ScheduledLocal.ToString("o"));
      changes.AddChange("scheduled", upgrade.ScheduledLocal.ToUniversalTime().ToString("yyyy-MM-dd'T'HH:mm:ss"));
      changes.AddChange("status", UpgradeStatus.Pending.ToString());
      var request = new UpdateItemRequest()
      {
        TableName = TableName,
        Key = new()
          {
              { "serialNumber", new AttributeValue(upgrade.SerialNumber) },
              { "upgradePath", new AttributeValue(upgrade.UpgradePath) }
          },
        AttributeUpdates = changes
      };

      // updates perform an insert if it doesn't exist
      var response = await Client.UpdateItemAsync(request);

      if (response.HttpStatusCode == System.Net.HttpStatusCode.OK)
      {
        Logger.LogInformation("Saved schedule");
        return true;
      }

      Logger.LogError("Unable to store schedule");
      Logger.LogError($"Offending JSON: {upgrade.SerializeCamel()}");

      return false;
    }
  }
}

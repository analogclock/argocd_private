using System.Collections.Generic;
using System.Threading.Tasks;
using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.DocumentModel;
using Amazon.DynamoDBv2.Model;
using FinsProvisioning.Extensions;
using FinsProvisioning.Models;

namespace FinsProvisioning.AwsExtensions
{
  public static class DynamoDbExtensions
  {
    /// <summary>
    /// Retrieve a DynamoDB item by its serial number
    /// </summary>
    /// <param name="dynamoDb">Client to use</param>
    /// <param name="tableName">The given table to get the item from</param>
    /// <param name="serialNumber">The given serial number to retrieve data for</param>
    /// <returns></returns>
    public static async Task<GetItemResponse> GetBySerialNumberAsync(this IAmazonDynamoDB dynamoDb, string tableName, string serialNumber)
    {
      var request = new GetItemRequest(tableName, new Dictionary<string, AttributeValue>
        {
          {"serialNumber", new AttributeValue(serialNumber)}
        });

      var response = await dynamoDb.GetItemAsync(request);

      return response;
    }

    public static async Task<List<T>> All<T>(this IAmazonDynamoDB dynamoDb, ScanRequest request)
    {
      ScanResponse response;
      var updates = new List<T>();
      do
      {
        response = await dynamoDb.ScanAsync(request);
        foreach (var item in response.Items)
        {
          var doc = Document.FromAttributeMap(item);
          var mod = doc.ToJson().DeserializeCamel<T>();
          updates.Add(mod);
        }

        request.ExclusiveStartKey = response.LastEvaluatedKey;
      } while (response.LastEvaluatedKey.Count != 0);

      return updates;
    }

    public static async Task<List<T>> GetAllBySerialNumber<T>(this IAmazonDynamoDB dynamoDB, string tableName, string serialNumber)
    {

      var request = new QueryRequest()
      {
        TableName = tableName,
        KeyConditionExpression = "serialNumber = :serialNumber",
        ExpressionAttributeValues = new() { { ":serialNumber", new AttributeValue(serialNumber) } }
      };

      QueryResponse response;
      var updates = new List<T>();
      do
      {
        response = await dynamoDB.QueryAsync(request);
        foreach (var item in response.Items)
        {
          var doc = Document.FromAttributeMap(item);
          var mod = doc.ToJson().DeserializeCamel<T>();
          updates.Add(mod);
        }
      } while (response.LastEvaluatedKey.Count > 0);

      return updates;
    }

    public static async Task<List<UpdateModel>> GetAllByVersion(this IAmazonDynamoDB dynamoDb, string tableName, string version)
    {
      var request = new ScanRequest(tableName)
      {
        ExpressionAttributeValues = new Dictionary<string, AttributeValue> {
          { ":version", new AttributeValue { S = version } }
        },
        FilterExpression = "contains(currentVersion, :version)",
      };

      return await dynamoDb.All<UpdateModel>(request);
    }

    public static async Task<bool> ExistsByPartitionKey(this IAmazonDynamoDB dynamoDb, string tableName, string keyName, string keyValue)
    {
      var request = new GetItemRequest(tableName, new Dictionary<string, AttributeValue>
        {
          {keyName, new AttributeValue(keyValue)}
        });

      var response = await dynamoDb.GetItemAsync(request);

      return response.IsItemSet;
    }
  }
}

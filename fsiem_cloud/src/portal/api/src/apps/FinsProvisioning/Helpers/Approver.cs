using System;
using System.Net;
using System.Threading.Tasks;
using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.DocumentModel;
using Amazon.DynamoDBv2.Model;
using FinsProvisioning.AwsExtensions;
using FinsProvisioning.Extensions;
using FinsProvisioning.Models;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace FinsProvisioning.Helpers
{
  public interface IApprover
  {
    Task<Approval> IsApprovedAsync(string serialNumber);
    Task<bool> AddAwaitingApprovalAsync(string serialNumber);
  }
  public class Approver : IApprover
  {
    private const string ApproverTableKey = "ApproverDynamoDbTable";
    private readonly IAmazonDynamoDB _dynamoDB;
    private readonly string _tableName;
    private readonly ILogger<Approver> _logger;

    public Approver(IAmazonDynamoDB dynamoDB,
      IConfiguration config,
      ILogger<Approver> logger)
    {
      _dynamoDB = dynamoDB ?? throw new ArgumentNullException(nameof(dynamoDB), "Error loading approver, dynamo db is null");
      _logger = logger ?? throw new ArgumentNullException(nameof(_logger), "Error loading logger for approver");
      _tableName = config[ApproverTableKey];
    }

    public async Task<bool> AddAwaitingApprovalAsync(string serialNumber)
    {
      var approval = new Approval(serialNumber);
      var doc = approval.ToDocument();

      var request = new PutItemRequest(_tableName, doc.ToAttributeMap());

      var put = await _dynamoDB.PutItemAsync(request);

      // we have failed to put item into the database
      if (put.HttpStatusCode != HttpStatusCode.OK)
      {
        _logger.LogError($"Unable to add item to table {_tableName}");
        _logger.LogError($"Offending JSON: {approval.ToJsonString()}");
        return false;
      }

      return true;
    }

    public async Task<Approval> IsApprovedAsync(string serialNumber)
    {
      try
      {
        _logger.LogInformation($"Checking approval for: {serialNumber}");
        var response = await _dynamoDB.GetBySerialNumberAsync(_tableName, serialNumber);
        if (!response.IsItemSet)
        {
          _logger.LogError($"Unable to find item with key: {serialNumber}, from table: {_tableName}");
          return null;
        }

        _logger.LogInformation($"Item found with serial number: {serialNumber}");
        var doc = Document.FromAttributeMap(response.Item);
        return doc.ToJson().DeserializeCamel<Approval>();
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, $"Error getting item: {ex.Message}");
        return null;
      }
    }
  }
}

using System;
using Amazon.DynamoDBv2;
using Microsoft.Extensions.Logging;

namespace FinsProvisioning.Services
{
  public class BaseService<T>
  {
    protected IAmazonDynamoDB Client;
    protected string TableName;
    protected ILogger<T> Logger;

    protected BaseService(IAmazonDynamoDB client, string tableName, ILogger<T> logger)
    {
      Client = client ?? throw new ArgumentNullException(nameof(client), "Null dynamodb client");
      TableName = tableName ?? throw new ArgumentNullException(nameof(tableName), "Table provided cannot be null");
      Logger = logger ?? throw new ArgumentNullException(nameof(client), "Null logger");
    }
  }
}

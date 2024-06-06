using System.Collections.Generic;
using System.Threading.Tasks;
using Amazon.DynamoDBv2;
using FinsProvisioning.AwsExtensions;
using FinsProvisioning.Models;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace FinsProvisioning.Services
{
  public interface IUpdateService
  {
    Task<bool> HasPath(string path);
    Task<List<UpdateModel>> CheckForUpdateAsync(string version);
  }

  public class UpdateService : BaseService<UpdateService>, IUpdateService
  {
    public UpdateService(
      IAmazonDynamoDB client,
      IConfiguration config,
      ILogger<UpdateService> logger
      ) : base(client, config["UpdateDynamoDbTable"], logger)
    { }

    public async Task<bool> HasPath(string path)
    {
      Logger.LogInformation("Getting upgrade by its path: {}", path);
      return await Client.ExistsByPartitionKey(TableName, "upgradePath", path);
    }

    public async Task<List<UpdateModel>> CheckForUpdateAsync(string version)
    {
      Logger.LogInformation($"Getting item starting with: {version}");
      var response = await Client.GetAllByVersion(TableName, version);

      return response;
    }
  }
}

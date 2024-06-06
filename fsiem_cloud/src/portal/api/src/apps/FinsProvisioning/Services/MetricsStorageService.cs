using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.DocumentModel;
using FinsProvisioning.AwsExtensions;
using FinsProvisioning.Extensions;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;

namespace FinsProvisioning.Services
{
  public interface IMetricsStorageService
  {
    Task<PartitionSize> Get(string serialNumber);
  }

  public class MetricsStorageService : BaseService<MetricsStorageService>, IMetricsStorageService
  {
    public MetricsStorageService(
      IAmazonDynamoDB client,
      IConfiguration config,
      ILogger<MetricsStorageService> logger
      ) : base(client, config["MetricsStorageDynamoDbTable"], logger)
    { }

    private static List<PartitionSizeStatDto> ParseCompressedPartitionSize(string input)
    {
      var compressed = Convert.FromBase64String(input);
      var payload = Encoding.UTF8.GetString(GZipHelper.Decompress(compressed));
      return JsonConvert.DeserializeObject<List<PartitionSizeStatDto>>(payload);
    }

    public async Task<PartitionSize> Get(string serialNumber)
    {
      Logger.LogInformation("Getting external storage by its serial number: {}", serialNumber);
      var response = await Client.GetBySerialNumberAsync(TableName, serialNumber);
      if (!response.IsItemSet)
      {
        Logger.LogError($"Unable to find item with key: {serialNumber}, from table: {TableName}");
        return null;
      }

      Logger.LogInformation($"Item found with serial number: {serialNumber}");
      var doc = Document.FromAttributeMap(response.Item);
      var partSizeDto = doc.ToJson().DeserializeCamel<PartitionSizeDto>();
      var online = ParseCompressedPartitionSize(partSizeDto.OnlineGzip);
      var archive = ParseCompressedPartitionSize(partSizeDto.ArchiveGzip);
      var resp = new PartitionSize(serialNumber, partSizeDto.LastUpdated, online, archive);
      Logger.LogInformation($"Resp: {JsonConvert.SerializeObject(resp)}");
      return resp;
    }
  }
}

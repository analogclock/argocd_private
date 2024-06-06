using System;
using System.IO;
using System.Threading.Tasks;
using Amazon.S3;
using Amazon.S3.Model;
using FinsProvisioning.Models;
using Newtonsoft.Json;

namespace FinsProvisioning.Helpers.Caches
{
  public class S3CommonDataCache : ICommonDataCache
  {
    private readonly IAmazonS3 _s3Client;
    private readonly string _bucket;
    private readonly string _key;

    public S3CommonDataCache(IAmazonS3 s3Client, string bucket, string key)
    {
      _s3Client = s3Client;
      _bucket = bucket;
      _key = key;
    }

    public async Task<bool> CreateAsync(Menu portals)
    {
      var content = JsonConvert.SerializeObject(portals);

      var response = await _s3Client.PutObjectAsync(new PutObjectRequest()
      {
        ContentBody = content,
        BucketName = _bucket,
        Key = _key,
        ContentType = "application/json"
      });

      return response.HttpStatusCode == System.Net.HttpStatusCode.OK;
    }

    public bool Exists()
    {
      try
      {
        var response = _s3Client.GetObjectMetadataAsync(_bucket, _key).Result;
        if (response.HttpStatusCode == System.Net.HttpStatusCode.NotFound)
          return false;

        return true;
      }

      catch (AmazonS3Exception ex)
      {
        if (ex.StatusCode == System.Net.HttpStatusCode.NotFound)
          return false;

        //status wasn't not found, so throw the exception
        throw;
      }
    }

    public async Task<Menu> GetAsync()
    {
      try
      {
        var getResponse = await _s3Client.GetObjectAsync(new GetObjectRequest()
        {
          BucketName = _bucket,
          Key = _key
        });

        string portalContent = null;
        using (var responseStream = getResponse.ResponseStream)
        using (var reader = new StreamReader(responseStream))
        {
          portalContent = reader.ReadToEnd(); // Now you process the response body.
        }

        if (string.IsNullOrWhiteSpace(portalContent))
          return null;

        var resp = JsonConvert.DeserializeObject<Menu>(portalContent);
        return resp;

      }
      catch
      {
        // throw away until we have logging
        return null;
      }
    }

    public DateTimeOffset? LastUpdate()
    {
      try
      {
        var response = _s3Client.GetObjectMetadataAsync(_bucket, _key).Result;
        return new DateTimeOffset(response.LastModified);
      }
      catch
      {
        return null;
      }
    }
  }
}

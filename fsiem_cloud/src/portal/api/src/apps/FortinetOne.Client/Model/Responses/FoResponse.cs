using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace FortinetOne.Client.Model.Responses
{
  public interface IFoResponse
  {
    HttpResponseMessage HttpResp { get; set; }
    void Parse(string dataElementName);
  }

  /// <summary>
  /// Parent type for all FortiOne API responses
  /// </summary>
  /// <typeparam name="T"></typeparam>
  public class FoResponse<T> : IFoResponse
  {
    public int Status { get; set; }
    public string Message { get; set; }
    public int TotalRows { get; set; }
    public T Data { get; set; }
    public HttpResponseMessage HttpResp { get; set; }

    public virtual void Parse(string dataElementName)
    {
      // Only parse if we received successful response 
      if (HttpResp.IsSuccessStatusCode)
      {
        var content = HttpResp.Content.ReadAsStringAsync().Result;
        dynamic json = JsonConvert.DeserializeObject(content);
        Status = Convert.ToInt32(json.d.status);
        Message = Convert.ToString(json.d.message);
        TotalRows = Convert.ToInt32(json.d.total_row);
        string tmp = json.d[dataElementName].ToString();

        var settings = new JsonSerializerSettings
        {
          DateParseHandling = DateParseHandling.DateTimeOffset
        };

        Data = JsonConvert.DeserializeObject<T>(tmp, settings);
      }
    }
  }

  public class Error
  {
    public string Code { get; set; }
    public string Message { get; set; }
    public string Reference { get; set; }
  }

  /// <summary>
  /// Parent type for all FortiCloud version 3 Responses
  /// </summary>
  /// <typeparam name="T"></typeparam>
  public class FoResponseV3<T> : FoResponse<T>
  {
    public DateTimeOffset ServerTime { get; set; }
    public bool IsError { get; set; }
    public List<Error> Error { get; set; }

    public FoResponseV3()
    {
      Error = new List<Error>();
    }
    /// <summary>
    /// Parse standard version 3 method
    /// </summary>
    /// <param name="dataElementName"></param>
    public override void Parse(string dataElementName)
    {
      // Only parse if we received successful response 
      if (HttpResp.IsSuccessStatusCode)
      {
        var content = HttpResp.Content.ReadAsStringAsync().Result;
        dynamic json = JsonConvert.DeserializeObject(content);
        Status = Convert.ToInt32(json.d.status.return_code);
        Message = Convert.ToString(json.d.status.message);
        try
        {
          ServerTime = DateTimeOffset.Parse(json.d.status.server_time);
        }
        catch
        {
          // we cannot parse what is returned - lets set it to 
          // UtcNow
          ServerTime = DateTimeOffset.UtcNow;
        }

        // unsupported
        TotalRows = 0;

        string tmp = json.d[dataElementName].ToString();

        var settings = new JsonSerializerSettings
        {
          DateParseHandling = DateParseHandling.DateTimeOffset
        };

        Data = JsonConvert.DeserializeObject<T>(tmp, settings);

      }
      else if (HttpResp.StatusCode != HttpStatusCode.InternalServerError)
      {
        var content = HttpResp.Content.ReadAsStringAsync().Result;
        dynamic json = JsonConvert.DeserializeObject(content);
        if (json.d.error != null)
        {
          IsError = true;
          foreach (var err in json.d.error)
          {
            var localErr = err as dynamic;
            Error.Add(new Error()
            {
              Code = localErr.code,
              Message = localErr.message,
              Reference = localErr.reference
            });
          }
        }
      }
    }

    public async Task<string> PrintResponseAsync()
    {
      if (HttpResp == null)
        return string.Empty;

      var builder = new StringBuilder();
      builder.AppendLine($"attempted to call: {HttpResp.RequestMessage.RequestUri}");
      builder.AppendLine("Request: ");
      builder.AppendLine($"{await HttpResp.RequestMessage.Content.ReadAsStringAsync()}");
      builder.AppendLine("Response: ");
      builder.AppendLine(await HttpResp.Content.ReadAsStringAsync());
      return builder.ToString();
    }
  }
}

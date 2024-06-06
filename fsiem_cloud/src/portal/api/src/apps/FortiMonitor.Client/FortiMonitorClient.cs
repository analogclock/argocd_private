using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace FortiMonitor.Client
{
  public interface IFortiMonitorClient
  {
    Task<List<string>> GetServerIDAsync(string serialNo, string role);
    Task<List<string>> GetMetricIDAsync(string serverID, string metricName);
    Task<List<KeyValuePair<DateTimeOffset, double>>> GetMetricDataAsync(string serverID,
      string metricID,
      string metricName,
      MetricTime time = MetricTime.Hour
    );
  }

  public class FortiMonitorClient : HttpClient, IFortiMonitorClient
  {
    private readonly string _baseApiUrl;
    private readonly string _environment;

    public FortiMonitorClient(string apiUrl = "",
      string token = "",
      string environment = "playground",
      int timeoutSeconds = 100)
    {
      _baseApiUrl = apiUrl;
      DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("ApiKey", token);
      _environment = environment;
      Timeout = TimeSpan.FromSeconds(timeoutSeconds);
    }

    public async Task<List<string>> GetServerIDAsync(string serialNo, string role)
    {
      var parameters = new Dictionary<string, string>()
      {
        {"limit", "50"},
        {"tag_filter_mode", "and"},
        {"tags", $"{serialNo},{role}"},
        {"attributes", $"Environment:{_environment}"},
        {"full", "true"}
      };

      var resp = await GetRequestAsync("server", parameters);

      // Loop over server responses and get IDs for each server
      var idList = new List<string>();
      foreach (var server in resp?["server_list"] ?? new JObject())
      {
        var url = server["url"]?.ToObject<string>() ?? "";
        var id = url.Substring(url.LastIndexOf('/') + 1);
        idList.Add(id);
      }

      return idList;
    }

    public async Task<List<string>> GetMetricIDAsync(string serverID, string metricName)
    {
      var parameters = new Dictionary<string, string>(){
        {"limit", "100"},
        {"name", metricName}
      };
      var resp = await GetRequestAsync($"server/{serverID}/agent_resource", parameters);
      var idList = new List<string>();
      foreach (var agentResource in resp?["agent_resource_list"] ?? new JObject())
      {
        var url = agentResource["url"]?.ToObject<string>() ?? "";
        var id = url.Substring(url.LastIndexOf('/') + 1);
        idList.Add(id);
      }

      return idList;
    }

    public async Task<List<KeyValuePair<DateTimeOffset, double>>> GetMetricDataAsync(string serverID,
      string metricID, string metricName, MetricTime time = MetricTime.Hour)
    {
      var parameters = new Dictionary<string, string>();
      var resp = await GetRequestAsync($"server/{serverID}/agent_resource/{metricID}/metric/{time.ToString().ToLowerInvariant()}", parameters);
      var data = resp?["data"];

      var metricList = new List<string>();
      foreach (var item in data ?? new JObject())
      {
        var propName = ((JProperty)item).Name;
        if (propName.Contains(metricName))
        {
          var metricData = resp?["data"]?[propName]?.FirstOrDefault();
          metricList = metricData?["data"]?.ToObject<List<string>>() ?? new List<string>();
        }
      }

      var labels = resp?["labels"]?.ToObject<List<string>>() ?? new List<string>();

      var metricsMap = Enumerable.Zip(
        labels, metricList,
        (key, value) =>
        {
          if (double.TryParse(value, out var dbl))
          {
            return new KeyValuePair<DateTimeOffset, double>(DateTimeOffset.FromUnixTimeSeconds(long.Parse(key)), dbl);
          }

          return new KeyValuePair<DateTimeOffset, double>(DateTimeOffset.FromUnixTimeSeconds(long.Parse(key)), 0);
        }
      ).ToList();
      return metricsMap;
    }

    private async Task<JObject> GetRequestAsync(string relativeApiPath, Dictionary<string, string> parameters)
    {
      var url = $"{_baseApiUrl}/{relativeApiPath}";
      var p = await new FormUrlEncodedContent(parameters).ReadAsStringAsync();
      var httpResp = await GetStringAsync($"{url}?{p}");

      return JsonConvert.DeserializeObject<JObject>(httpResp) ?? new JObject();
    }
  }
};

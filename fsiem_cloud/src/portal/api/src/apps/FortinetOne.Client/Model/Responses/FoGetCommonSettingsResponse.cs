using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace FortinetOne.Client.Model.Responses
{
  public class FoCommonSettingsResponse : FoResponse<List<FoCommonSettings>>
  {
  }
  public class FoCommonSettings
  {
    [JsonProperty("category")]
    public string Category { get; set; }
    [JsonProperty("key")]
    public string Key { get; set; }
    [JsonProperty("value")]
    public string Value { get; set; }
    [JsonProperty("last_updated_time")]
    public DateTimeOffset LastUpdatedTime { get; set; }
  }
}

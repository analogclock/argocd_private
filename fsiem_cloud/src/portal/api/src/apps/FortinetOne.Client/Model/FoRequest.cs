using Newtonsoft.Json;

namespace FortinetOne.Client.Model
{
  public class FoRequestData
  {
    [JsonProperty(PropertyName = "__type")]
    public string Type { get; set; }

    //[JsonProperty(PropertyName = "__version")]
    //public string Version { get; set; } = FoApiVersion.Version;

    [JsonProperty(PropertyName = "request_channel")]
    public string RequestChannel { get; set; } = "FortiSIEMCloud";

    //[JsonProperty(PropertyName = "search_filters", NullValueHandling = NullValueHandling.Ignore)]
    //public FoSearchFilters SearchFilters { get; set; }

    [JsonIgnore]
    public string RelativePath { get; set; }

    public void AddRelativePath(string relativePath)
    {
      RelativePath = relativePath;
    }

    public void AddRequestType(string requestType)
    {
      Type = requestType;
    }
  }

  public class FoRequest
  {
    // An interesting FortiOne API quirk :P
    [JsonProperty(PropertyName = "d")]
    public FoRequestData Data { get; set; }

    public FoRequest()
    {
      Data = new FoRequestData();
    }
  }
}

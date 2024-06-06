using System;
using Newtonsoft.Json;

namespace FortinetOne.Client.Model.Responses
{

  public class FoCommonDataLastUpdateTimeResponse : FoResponseV3<FoCommonDataLastUpdateTimeDetails>
  {
  }

  public class FoCommonDataLastUpdateTimeDetails
  {
    // {
    //   "last_updated_time": "2021-01-04T13:53:29-08:00"
    // }

    [JsonProperty("last_updated_time")]
    public DateTimeOffset LastUpdatedTime { get; set; }

    public FoCommonDataLastUpdateTimeDetails()
    { }
  }
}

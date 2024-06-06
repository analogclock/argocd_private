using System;
using Newtonsoft.Json;

namespace FortinetOne.Client.Model.Responses
{
  public class FoGetFortiCloudPremiumSubscriptionResponse : FoResponseV3<FoGetFortiCloudPremiumSubscription>
  {
  }

  public class FoGetFortiCloudPremiumSubscription
  {
    //{
    //    "hasSubscription": true,
    //    "startDate": "2019-12-17T00:00:00.0000000",
    //    "endDate": "2020-12-16T00:00:00",
    //    "status": "Active",
    //    "serviceDescription": "FortiCloud Premium Subscription"
    //}
    [JsonProperty("hasSubscription")]
    public bool? HasSubscription { get; set; } = null;

    [JsonProperty("startDate")]
    public DateTimeOffset? StartDate { get; set; } = null;

    [JsonProperty("endDate")]
    public DateTimeOffset? EndDate { get; set; } = null;

    [JsonProperty("status")]
    public string Status { get; set; } = string.Empty;

    [JsonProperty("serviceDescription")]
    public string ServiceDescription { get; set; } = string.Empty;

    public FoGetFortiCloudPremiumSubscription()
    {
    }
  }
}

using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace FortinetOne.Client.Model.Responses
{
  /// <summary>
  /// Response for GetProductSupportQuantity
  /// HTTP POST /FortinetOneProductService.asmx/Process
  /// </summary>
  public class FoProductSupportQuantityResponse : FoResponse<List<FoProductSupportQuantityResponseData>>
  {
  }

  public class FoProductSupportQuantityResponseData
  {
    [JsonProperty(PropertyName = "account_id")]
    public int AccountId { get; set; }

    [JsonProperty(PropertyName = "user_id")]
    public int UserId { get; set; }

    [JsonProperty(PropertyName = "serial_number")]
    public string SerialNumber { get; set; }

    [JsonProperty(PropertyName = "quantity")]
    public int Quantity { get; set; }

    [JsonProperty(PropertyName = "type")]
    public int Type { get; set; }

    [JsonProperty(PropertyName = "type_desc")]
    public string TypeDescription { get; set; }

    [JsonProperty(PropertyName = "end_date")]
    public DateTimeOffset EndDate { get; set; }
  }
}

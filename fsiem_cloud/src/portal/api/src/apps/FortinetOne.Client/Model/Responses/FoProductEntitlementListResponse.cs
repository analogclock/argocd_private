using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace FortinetOne.Client.Model.Responses
{
  /// <summary>
  /// Response for GetProductEntitlementList
  /// HTTP POST /FortinetOneProductService.asmx/Process
  /// </summary>
  public class FoProductEntitlementListResponse : FoResponse<FoProductEntitlementListResponseData>
  {
  }

  public class FoProductEntitlementListResponseData
  {
    [JsonProperty(PropertyName = "account_id")]
    public int AccountId { get; set; }

    [JsonProperty(PropertyName = "assets")]
    public List<FoAsset> Assets { get; set; }

    public FoProductEntitlementListResponseData()
    {
      Assets = new List<FoAsset>();
    }
  }

  public class FoAsset
  {
    [JsonProperty(PropertyName = "serial_number")]
    public string SerialNumber { get; set; }

    [JsonProperty(PropertyName = "description")]
    public string Description { get; set; }

    [JsonProperty(PropertyName = "entitlements")]
    public List<FoEntitlement> Entitlements { get; set; }

    public FoAsset()
    {
      Entitlements = new List<FoEntitlement>();
    }
  }

  public class FoEntitlement
  {
    [JsonProperty(PropertyName = "terms")]
    public List<FoEntitlementTerm> Terms { get; set; }

    public FoEntitlement()
    {
      Terms = new List<FoEntitlementTerm>();
    }
  }

  public class FoEntitlementTerm
  {
    [JsonProperty(PropertyName = "level")]
    public int Level { get; set; }

    [JsonProperty(PropertyName = "level_desc")]
    public string LevelDescription { get; set; }

    [JsonProperty(PropertyName = "type")]
    public int Type { get; set; }

    [JsonProperty(PropertyName = "type_desc")]
    public string TypeDescription { get; set; }

    [JsonProperty(PropertyName = "quantity")]
    public int Quantity { get; set; }

    [JsonProperty(PropertyName = "start_date")]
    public DateTimeOffset StartDate { get; set; }

    [JsonProperty(PropertyName = "end_date")]
    public DateTimeOffset EndDate { get; set; }
  }
}

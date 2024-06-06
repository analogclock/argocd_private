using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace FortinetOne.Client.Model.Responses
{
  public class FoFortiSIEMCloudResponse : FoResponseV3<List<FoFortiSIEMCloudResponseData>>
  {
  }

  public class FoFortiSIEMCloudResponseData
  {
    // raw json returned by FortiCloud API -- currently expected
    // TODO: Update this when API is live

    //{
    // "serialNumber": "FSMCLD0000000001"
    // "description": "FortiSIEM Cloud",
    // "entitlements": [ // all active contracts are set in here
    //   {
    //     "contractNumber": null,
    //     "supportType": 224,
    //     "supportTypeDesc": "FSM Compute",
    //     "supportLevel": 6,
    //     "supportLevelDesc": "Web/Online",
    //     "startDate": "2020-06-25T17:23:49",
    //     "endDate": "2021-06-25T17:23:49",
    //     "quantity": 123
    //   },
    //   {
    //     "contractNumber": null,
    //     "supportType": 225,
    //     "supportTypeDesc": "FSM Online Storage",
    //     "supportLevel": 6,
    //     "supportLevelDesc": "Web/Online",
    //     "startDate": "2020-06-25T17:23:49",
    //     "endDate": "2021-06-25T17:23:49",
    //     "quantity": 123
    //   },
    //   {
    //     "contractNumber": null,
    //     "supportType": 226,
    //     "supportTypeDesc": "FSM Archive Storage",
    //     "supportLevel": 6,
    //     "supportLevelDesc": "Web/Online",
    //     "startDate": "2020-06-25T17:23:49",
    //     "endDate": "2021-06-25T17:23:49",
    //     "quantity": 123
    //   }
    // ],
    // "assetTreePath": null,
    // "assetGroup": [
    //   {
    //     "name": "Group 1"
    //   }
    // ]
    //}

    [JsonProperty(PropertyName = "serialNumber")]
    public string SerialNumber { get; set; } = string.Empty;

    [JsonProperty(PropertyName = "description")]
    public string Description { get; set; } = string.Empty;

    [JsonProperty(PropertyName = "entitlements")]
    public List<Term> Entitlements { get; set; } = new List<Term>();

    [JsonProperty(PropertyName = "assetTreePath")]
    public object AssertTreePath { get; set; }

    [JsonProperty(PropertyName = "assetGroup")]
    public List<AssetGroup> AssetGroup { get; set; } = new List<AssetGroup>();
  }

  public class AssetGroup
  {
    [JsonProperty(PropertyName = "name")]
    public string Name { get; set; }
  }

  // {
  //   "contractNumber": null,
  //   "supportType": 226,
  //   "supportTypeDesc": "FSM Archive Storage",
  //   "supportLevel": 6,
  //   "supportLevelDesc": "Web/Online",
  //   "startDate": "2020-06-25T17:23:49",
  //   "endDate": "2021-06-25T17:23:49",
  //   "quantity": 123
  // }
  public class Term
  {
    [JsonProperty(PropertyName = "supportLevel")]
    public int SupportLevel { get; set; }

    [JsonProperty(PropertyName = "supportLevelDesc")]
    public string SupportLevelDescription { get; set; }

    [JsonProperty(PropertyName = "supportType")]
    public int SupportType { get; set; }

    [JsonProperty(PropertyName = "supportTypeDesc")]
    public string SupportTypeDescription { get; set; }

    [JsonProperty(PropertyName = "startDate")]
    public DateTimeOffset StartDate { get; set; }

    [JsonProperty(PropertyName = "endDate")]
    public DateTimeOffset EndDate { get; set; }

    [JsonProperty(PropertyName = "quantity")]
    public int Quantity { get; set; }
  }
}

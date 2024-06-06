using System;
using Newtonsoft.Json;

namespace FortinetOne.Client.Model.Responses
{
  public class FoGetAPIPermissionsResponse : FoResponseV3<FoGetAPIPermissionsResponseData>
  {
  }

  public class FoGetAPIPermissionsResponseData
  {
    // raw json returned by FortiCloud API
    //{
    //  "account_id": 12345,
    //  "api_user_id": "7e574d12-cec8-401b-9fa6-61777e299037",
    //  "token_expiration": "2020-08-15 12:23:05",
    //  "permission": "ReadOnly",
    //  "status": "Active"
    //}

    [JsonProperty(PropertyName = "account_id")]
    public int? AccountId { get; set; } = null;

    [JsonProperty(PropertyName = "api_user_id")]
    public string ApiUserId { get; set; } = string.Empty;

    [JsonProperty(PropertyName = "token_expiration")]
    public DateTimeOffset? TokenExpiration { get; set; } = null;

    [JsonProperty(PropertyName = "permission")]
    public string Permission { get; set; } = string.Empty;

    [JsonProperty(PropertyName = "status")]
    public string Status { get; set; } = string.Empty;
  }
}

using System.Collections.Generic;
using Newtonsoft.Json;

namespace FortinetOne.Client.Model.Responses
{
  public class FoGetAccountsByEmailResponse : FoResponseV3<List<FoAccountsByEmail>>
  {
  }

  public class FoAccountsByEmail
  {
    // raw json returned by FortiCloud API
    //{
    //  "account_id": 5982,
    //  "account_email": "nguo@fortinet.com",
    //  "master_user_name": "Ning Guo",
    //  "account_company": "Fortinet, Inc.",
    //  "user_id": -1,
    //  "user_email": "nguo@fortinet.com",
    //  "user_name": null,
    //  "is_master_user": true,
    //  "user_status": "Active",
    //  "account_tags": [
    //    "Disable Cloud Key validation",
    //    "Disable all cloud services"
    //  ],
    //  "account_portal_access": true,
    //  "user_fullaccess": false,
    //  "user_portal_access": false,
    //  "iam_account_name": null,
    //  "is_2fa_enforced": false,
    //  "failed_2fa_message": "Using 2 factor authentication has been mandated by your account administrator. Please go to <a href=\\\"....\\\">2FA setup page</a>.",
    //  "all_assets_access": true,
    //  "portals_access": [
    //    {
    //      "app_id": 19,
    //      "app_name": "FortiAnalyzerCloud",
    //      "user_role": "Portal_Admin",
    //      "is_allow_access": true,
    //      "user_permission": "ReadWrite",
    //      "visibility": "ShowEnabled"
    //    }
    //  ]
    //}

    [JsonProperty(PropertyName = "account_id")]
    public int? AccountId { get; set; } = null;

    [JsonProperty(PropertyName = "account_email")]
    public string AccountEmail { get; set; } = string.Empty;

    [JsonProperty(PropertyName = "master_user_name")]
    public string MasterUserName { get; set; } = string.Empty;

    [JsonProperty(PropertyName = "account_company")]
    public string AccountCompany { get; set; } = string.Empty;

    [JsonProperty(PropertyName = "user_id")]
    public int? UserId { get; set; } = null;

    [JsonProperty(PropertyName = "user_email")]
    public string UserEmail { get; set; } = string.Empty;

    [JsonProperty(PropertyName = "user_name")]
    public string UserName { get; set; } = string.Empty;

    [JsonProperty(PropertyName = "user_status")]
    public string UserStatus { get; set; } = string.Empty;

    [JsonProperty(PropertyName = "is_master_user")]
    public bool? IsMasterUser { get; set; } = null;

    [JsonProperty(PropertyName = "account_tags")]
    public List<string> AccountTags { get; set; } = new List<string>();

    [JsonProperty(PropertyName = "account_portal_access")]
    public bool? AccountPortalAccess { get; set; } = null;

    [JsonProperty(PropertyName = "user_fullaccess")]
    public bool? UserFullAccess { get; set; } = null;

    [JsonProperty(PropertyName = "user_portal_access")]
    public bool? UserPortalAccess { get; set; } = null;

    [JsonProperty(PropertyName = "iam_account_name")]
    public string IAMAccountName { get; set; } = string.Empty;

    [JsonProperty(PropertyName = "is_2fa_enforced")]
    public bool? Is2FAEnforced { get; set; } = null;

    [JsonProperty(PropertyName = "failed_2fa_message")]
    public string Failed2FAMessage { get; set; } = string.Empty;

    [JsonProperty(PropertyName = "all_assets_access")]
    public bool? AllAssestsAccess { get; set; } = null;

    [JsonProperty(PropertyName = "portals_access")]
    public List<FoPortalPermission> PortalsAccess { get; set; } = new List<FoPortalPermission>();
  }
}

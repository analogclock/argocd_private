using System.Collections.Generic;
using Newtonsoft.Json;

namespace FortinetOne.Client.Model.Responses
{
  public class FoGetUserPermissionsResponse : FoResponseV3<List<FoGetUserPermissionsResponseData>>
  {
  }

  public class FoGetUserPermissionsResponseData
  {
    // raw json returned by FortiCloud API
    //{
    //        "account_id": 923180,
    //        "account_email": "dhart@fortinet.com",
    //        "account_company": "ACME Ltd",
    //        "user_id": -1,
    //        "user_email": null,
    //        "user_name": null,
    //        "is_master_user": true,
    //        "master_user_name": "Darren Hart",
    //        "iam_user_name": null,
    //        "iam_account_name": "923180",
    //        "user_group": null,
    //        "all_assets_access": true,
    //        "user_auth_passed": true,
    //        "user_auth_url": null,
    //        "portals": [
    //            {
    //                "app_id": 1,
    //                "app_name": "FortiCASB",
    //                "user_role": "Portal_Admin",
    //                "is_allow_access": true,
    //                "user_permission": null,
    //                "visibility": "ShowEnabled"
    //            }
    //        ],
    //        "user_menu": [
    //            {
    //                "item_id": 10205,
    //                "visibility": "ShowEnabled"
    //            },
    //            {
    //                "item_id": 10208,
    //                "visibility": "Hide"
    //            }
    //        ],
    //        "support_menu": [
    //            {
    //                "item_id": 10005,
    //                "visibility": "ShowEnabled"
    //            }
    //        ]
    //    }

    [JsonProperty(PropertyName = "account_id")]
    public int? AccountId { get; set; } = null;

    [JsonProperty(PropertyName = "account_email")]
    public string AccountEmail { get; set; } = null;

    [JsonProperty(PropertyName = "account_company")]
    public string AccountCompany { get; set; } = null;

    [JsonProperty(PropertyName = "master_user_name")]
    public string MasterUserName { get; set; } = null;

    [JsonProperty(PropertyName = "is_master_user")]
    public bool? IsMasterUser { get; set; } = null;

    [JsonProperty(PropertyName = "user_id")]
    public int? UserId { get; set; } = null;

    [JsonProperty(PropertyName = "user_email")]
    public string UserEmail { get; set; } = string.Empty;

    [JsonProperty(PropertyName = "user_name")]
    public string UserName { get; set; } = string.Empty;

    [JsonProperty(PropertyName = "iam_user_name")]
    public string IAMUserName { get; set; } = string.Empty;

    [JsonProperty(PropertyName = "iam_account_name")]
    public string IAMAccountName { get; set; } = string.Empty;

    [JsonProperty(PropertyName = "user_group")]
    public string UserGroup { get; set; } = string.Empty;

    [JsonProperty(PropertyName = "all_assets_access")]
    public bool? AllAssestsAccess { get; set; } = null;

    [JsonProperty(PropertyName = "user_auth_passed")]
    public bool? UserAuthPassed { get; set; } = null;

    [JsonProperty(PropertyName = "user_auth_url")]
    public string UserAuthUrl { get; set; } = null;

    [JsonProperty(PropertyName = "portals")]
    public List<FoPortalPermission> Portals { get; set; } = new List<FoPortalPermission>();

    [JsonProperty(PropertyName = "user_menu")]
    public List<FoUserMenu> UserMenu { get; set; } = new List<FoUserMenu>();

    [JsonProperty(PropertyName = "support_menu")]
    public List<FoUserMenu> SupportMenu { get; set; } = new List<FoUserMenu>();
  }

  public class FoPortalPermission
  {
    // {
    //      "app_id": 1,
    //      "app_name": "FortiCASB",
    //      "user_role": "Portal_Admin",
    //      "is_allow_access": true,
    //      "user_permission": null,
    //      "visibility": "ShowEnabled"
    // }

    [JsonProperty(PropertyName = "app_id")]
    public int? AppId { get; set; } = null;

    [JsonProperty(PropertyName = "app_name")]
    public string AppName { get; set; } = string.Empty;

    [JsonProperty(PropertyName = "user_role")]
    public string UserRole { get; set; } = string.Empty;

    [JsonProperty(PropertyName = "is_allow_access")]
    public bool? IsAllowAccess { get; set; } = null;

    [JsonProperty(PropertyName = "user_permission")]
    public string UserPermission { get; set; } = string.Empty;

    [JsonProperty(PropertyName = "visibility")]
    public string Visibility { get; set; } = string.Empty;
  }

  public class FoUserMenu
  {
    //{
    //    "item_id": 10205,
    //    "visibility": "ShowEnabled"
    //}

    [JsonProperty(PropertyName = "item_id")]
    public int ItemId { get; set; }

    [JsonProperty(PropertyName = "visibility")]
    public string Visibility { get; set; } = string.Empty;
  }
}

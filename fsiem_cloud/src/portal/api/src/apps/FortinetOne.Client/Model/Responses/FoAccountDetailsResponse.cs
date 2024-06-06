using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace FortinetOne.Client.Model.Responses
{
  [Obsolete("will be removed during v3 upgrade", false)]
  public class FoAccountDetailsResponse : FoResponse<FoAccountDetails>
  {
  }

  [Obsolete("will be removed during v3 upgrade", false)]
  public class FoAccountDetails
  {
    [JsonProperty("account_id")]
    public int AccountId { get; set; }
    [JsonProperty("account_email")]
    public string AccountEmail { get; set; }
    [JsonProperty("master_user_name")]
    public string MasterUserName { get; set; }
    [JsonProperty("account_company")]
    public string AccountCompany { get; set; }
    [JsonProperty("is_super_account")]
    public bool IsSuperAccount { get; set; }
    [JsonProperty("users")]
    public List<FoAccount> Users { get; set; }

    public FoAccountDetails()
    {
      Users = new List<FoAccount>();
    }
  }

  public class FoAccountDetailsV3Response : FoResponseV3<FoAccountDetailsV3>
  {
  }

  public class FoAccountDetailsV3
  {
    //{
    //  "account_id": 156078,
    //  "account_email": "FCDemo_03@test.com",
    //  "master_user_name": "My Master User",
    //  "account_company": "company 156078",
    //  "is_super_account": true,
    //  "iam_account_name": "www",
    //  "is_2fa_enforced": false,
    //  "failed_2fa_message": "Using 2 factor authentication has been mandated by your account administrator. Please go to <a href=\\\"....\\\">2FA setup page</a>.",
    //  "users": []
    //}

    [JsonProperty("account_id")]
    public int? AccountId { get; set; } = null;

    [JsonProperty("account_email")]
    public string AccountEmail { get; set; } = string.Empty;

    [JsonProperty("master_user_name")]
    public string MasterUserName { get; set; } = string.Empty;

    [JsonProperty("account_company")]
    public string AccountCompany { get; set; }

    [JsonProperty("is_super_account")]
    public bool? IsSuperAccount { get; set; } = null;

    [JsonProperty("users")]
    public List<FoUserAccountV3> Users { get; set; } = new List<FoUserAccountV3>();

    public FoAccountDetailsV3()
    {
    }
  }

  public class FoUserAccountV3
  {
    //{
    //  "user_id": 31091,
    //  "user_email": "testbyls2@test.com",
    //  "user_name": "name 31091",
    //  "user_fullaccess": false,
    //  "iam_user_name": null,
    //  "user_group": null,
    //  "user_status": "Active",
    //  "all_assets_access": false,
    //  "is_email_validation_needed": false,
    //  "email_validation_needed_message": "You need to verify your email address before you can continue. Please go to <a href=\\\"....\\\">email validation page</a>.",
    //  "portals": []
    //}

    [JsonProperty("user_id")]
    public int? UserId { get; set; } = null;

    [JsonProperty("user_email")]
    public string UserEmail { get; set; } = string.Empty;

    [JsonProperty("user_name")]
    public string UserName { get; set; } = string.Empty;

    [JsonProperty("user_fullaccess")]
    public bool? UserFullAccess { get; set; } = null;

    [JsonProperty("iam_user_name")]
    public string IAMUserName { get; set; } = string.Empty;

    [JsonProperty("user_group")]
    public string UserGroup { get; set; } = string.Empty;

    [JsonProperty("user_status")]
    public string UserStatus { get; set; } = string.Empty;

    [JsonProperty("all_assets_access")]
    public bool? AllAssetsAccess { get; set; } = null;

    [JsonProperty("is_email_validation_needed")]
    public bool? IsEmailValidationNeeded { get; set; } = null;

    [JsonProperty("email_validation_needed_message")]
    public string EmailValidationNeededMessage { get; set; } = string.Empty;

    [JsonProperty("portals")]
    public List<FoPortalPermission> Portals { get; set; } = new List<FoPortalPermission>();
  }
}

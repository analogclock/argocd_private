using System.Collections.Generic;
using Newtonsoft.Json;

namespace FortinetOne.Client.Model.Responses
{
  public class FoLoginAccountsByEmailResponse : FoResponse<List<FoAccount>>
  {
  }

  public class FoAccount
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
    [JsonProperty("user_id")]
    public int UserId { get; set; }
    [JsonProperty("user_email")]
    public string UserEmail { get; set; }
    [JsonProperty("user_name")]
    public string UserName { get; set; }
    [JsonProperty("user_fullaccess")]
    public string UserFullacccess { get; set; }
    [JsonProperty("portals")]
    public List<FoAccountPortal> Portals { get; set; }

    public FoAccount()
    {
      Portals = new List<FoAccountPortal>();
    }
  }

  public class FoAccountPortal
  {
    [JsonProperty("app_name")]
    public string AppName { get; set; }
    [JsonProperty("user_role")]
    public string UserRole { get; set; }
    [JsonProperty("is_allow_access")]
    public bool IsAllowAccess { get; set; }
  }
}

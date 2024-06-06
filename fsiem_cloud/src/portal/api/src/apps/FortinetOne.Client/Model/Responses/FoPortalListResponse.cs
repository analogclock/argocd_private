using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace FortinetOne.Client.Model.Responses
{
  public class FoPortalListResponseV3 : FoResponseV3<List<FoPortal>> { }
  public class FoPortalListResponse : FoResponse<List<FoPortal>>
  {
  }
  public class FoPortal
  {
    [JsonProperty("app_name")]
    public string AppName { get; set; }
    [JsonProperty("app_category")]
    public string AppCategory { get; set; }
    [JsonProperty("section_header")]
    public string SectionHeader { get; set; }
    [JsonProperty("app_description")]
    public string AppDescription { get; set; }
    [JsonProperty("display_name")]
    public string DisplayName { get; set; }
    [JsonProperty("before_login_url")]
    public string BeforeLoginUrl { get; set; }
    [JsonProperty("login_url")]
    public string LoginUrl { get; set; }
    [JsonProperty("logout_url")]
    public string LogoutUrl { get; set; }
    [JsonProperty("displayed_in_banner")]
    public string DisplayedInBanner { get; set; }
    [JsonProperty("order")]
    public int Order { get; set; }
    [JsonProperty("image_content")]
    public string ImageContent { get; set; }
    [JsonProperty("app_id")]
    public int AppId { get; set; }
    [JsonProperty("lastupdate_date")]
    public DateTimeOffset LastUpdatedDate { get; set; }
  }
}

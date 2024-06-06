using System.Collections.Generic;
using Newtonsoft.Json;

namespace FortinetOne.Client.Model.Responses
{

  public class FoCommonDataResponse : FoResponseV3<FoCommonDataDetails>
  {
  }

  public class FoCommonDataDetails
  {
    //{
    //    "portal_menu_items": [
    //        {
    //            "app_id": 1,
    //            "app_name": "FortiCASB",
    //            "display_name": "FortiCASB",
    //            "description": "FortiCASB",
    //            "section_header": "Cloud Service",
    //            "url": "https://qa.staging.forticasb.com/ssoLogin",
    //            "order": 3040,
    //            "image_content": "...base64 image data..."
    //        }                
    //    ],
    //    "portal_menu_headers": [
    //        {
    //            "display_name": "Assets & Accounts",
    //            "description": "...",
    //            "url": "https://support-dev.corp.fortinet.com/",
    //            "order": 1
    //        }...
    //    ],
    //    "user_menu_items": [
    //        {
    //            "item_id": 10205,
    //            "display_name": "My Account",
    //            "description": "...",
    //            "url": "https://support-dev.corp.fortinet.com/account/",
    //            "order": 1,
    //            "image_content": "...base64 image data..."
    //        }
    //    ],
    //    "support_menu_headers": [
    //        {
    //            "display_name": "Downloads",
    //            "description": "...",
    //            "url": "https://support-dev.corp.fortinet.com/download/index.aspx",
    //            "order": 1
    //        }...
    //    ],
    //    "support_menu_items": [
    //        {
    //            "item_id": 10005,
    //            "display_name": "Firmware Download",
    //            "section_header": "Downloads",
    //            "description": "...",
    //            "url": "https://support-dev.corp.fortinet.com/download/Firmware.aspx",
    //            "order": 100,
    //            "image_content": "...base64 image data..."
    //        }
    //    ],
    //    "configurations": [
    //        {
    //            "name": "AccountCreation_URL",
    //            "value": "https://support-dev.corp.fortinet.com/Credentials/Account/AccountCreation.aspx"
    //        }
    //    ],
    //    "logos": [
    //        {
    //            "logo_id": 10300,
    //            "order": 1,
    //            "image_content": "...base64 image data..."
    //        },
    //        {
    //            "logo_id": 10305,
    //            "order": 5,
    //            "image_content": "...base64 image data..."
    //        }
    //    ]
    //}

    [JsonProperty("portal_menu_items")]
    public List<FoCommonPortalItem> PortalMenuItems { get; set; }

    [JsonProperty("portal_menu_headers")]
    public List<FoCommonHeaders> PortalMenuHeaders { get; set; }

    [JsonProperty("user_menu_items")]
    public List<FoCommonMenuItem> UserMenuItems { get; set; }

    [JsonProperty("support_menu_headers")]
    public List<FoCommonHeaders> SupportMenuHeaders { get; set; }

    [JsonProperty("support_menu_items")]
    public List<FoCommonMenuItem> SupportMenuItems { get; set; }

    [JsonProperty("configurations")]
    public List<FoCommonConfigurations> Configurations { get; set; }

    [JsonProperty("logos")]
    public List<FoCommonLogosItem> Logos { get; set; }

    public FoCommonDataDetails()
    {
    }
  }

  public class FoCommonConfigurations
  {
    // {
    //      "name": "AccountCreation_URL",
    //      "value": "https://support-dev.corp.fortinet.com/Credentials/Account/AccountCreation.aspx"
    // }

    [JsonProperty("name")]
    public string Name { get; set; }

    [JsonProperty("value")]
    public string Value { get; set; }
  }

  public class FoCommonItemImage
  {
    [JsonProperty("order")]
    public int Order { get; set; }

    [JsonProperty("image_content")]
    public string ImageContent { get; set; }
  }

  public class FoCommonItem : FoCommonItemImage
  {
    [JsonProperty("display_name")]
    public string DisplayName { get; set; }

    [JsonProperty("description")]
    public string Description { get; set; }

    [JsonProperty("url")]
    public string Url { get; set; }

    [JsonProperty("section_header")]
    public string SectionHeader { get; set; }
  }

  public class FoCommonPortalItem : FoCommonItem
  {
    //        {
    //            "app_id": 1, // we will update this to ItemId
    //            "app_name": "FortiCASB",
    //            "display_name": "FortiCASB",
    //            "description": "FortiCASB",
    //            "section_header": "Cloud Service",
    //            "url": "https://qa.staging.forticasb.com/ssoLogin",
    //            "order": 3040,
    //            "image_content": "...base64 image data..."
    //        }

    [JsonProperty("app_id")]
    public int AppId { get; set; }

    [JsonProperty("app_name")]
    public string AppName { get; set; }
  }

  public class FoCommonMenuItem : FoCommonItem
  {
    // {
    //     "item_id": 10205,
    //     "display_name": "My Account",
    //     "description": "...",
    //     "url": "https://support-dev.corp.fortinet.com/account/",
    //     "order": 1,
    //     "image_content": "...base64 image data..."
    // }

    [JsonProperty("item_id")]
    public int ItemId { get; set; }
  }

  public class FoCommonLogosItem : FoCommonItemImage
  {
    // {
    //     "logo_id": 10300,
    //     "order": 1,
    //     "image_content": "...base64 image data..."
    // },

    [JsonProperty("logo_id")]
    public int LogoId { get; set; }
  }

  public class FoCommonHeaders
  {
    //        {
    //            "display_name": "Assets & Accounts",
    //            "description": "...",
    //            "url": "https://support-dev.corp.fortinet.com/",
    //            "order": 1
    //        }

    [JsonProperty("display_name")]
    public string DisplayName { get; set; }

    [JsonProperty("description")]
    public string Description { get; set; }

    [JsonProperty("url")]
    public string Url { get; set; }

    [JsonProperty("order")]
    public int Order { get; set; }
  }
}

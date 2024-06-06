using System.Collections.Generic;
using System.Linq;
using FinsProvisioning.Models;
using FortinetOne.Client.Model.Responses;

namespace FinsProvisioning.FoResponseExtensions
{
  public static class FoCommonDataResponseEx
  {
    public static Menu ToMenu(this FoCommonDataResponse foPortalResponse)
    {
      var data = foPortalResponse.Data;

      return new Menu()
      {
        PortalMenuHeaders = data.PortalMenuHeaders.ToHeaders(),
        PortalMenuItems = data.PortalMenuItems.ToPortalItems(),
        SupportMenuHeaders = data.SupportMenuHeaders.ToHeaders(),
        SupportMenuItems = data.SupportMenuItems.ToItems(),
        UserMenuItems = data.UserMenuItems.ToItems(),
        Configurations = data.Configurations.ToConfigurations(),
        Logos = data.Logos.ToLogos()
      };
    }

    public static List<CommonLogosItem> ToLogos(this List<FoCommonLogosItem> logos)
    {
      return logos.Select(logo => logo.ToLogo()).ToList();
    }

    public static CommonLogosItem ToLogo(this FoCommonLogosItem item) => new CommonLogosItem()
    {
      ImageContent = item.ImageContent,
      LogoId = item.LogoId,
      Order = item.Order
    };

    public static List<CommonConfigurations> ToConfigurations(this List<FoCommonConfigurations> configs)
    {
      return configs.Select(config => config.ToConfiguration()).ToList();
    }

    public static CommonConfigurations ToConfiguration(this FoCommonConfigurations item) => new CommonConfigurations()
    {
      Name = item.Name,
      Value = item.Value
    };

    public static List<CommonPortalItem> ToPortalItems(this List<FoCommonPortalItem> portals)
    {
      return portals.Select(item => item.ToPortalItem()).ToList();
    }

    public static CommonPortalItem ToPortalItem(this FoCommonPortalItem item) => new CommonPortalItem()
    {
      Description = item.Description,
      DisplayName = item.DisplayName,
      Order = item.Order,
      Url = item.Url,
      ItemId = item.AppId,
      AppName = item.AppName,
      ImageContent = item.ImageContent,
      SectionHeader = item.SectionHeader
    };

    public static List<CommonHeaders> ToHeaders(this List<FoCommonHeaders> headers)
    {
      return headers.Select(header => header.ToHeader()).ToList();
    }

    public static CommonHeaders ToHeader(this FoCommonHeaders header) => new CommonHeaders()
    {
      Description = header.Description,
      DisplayName = header.DisplayName,
      Order = header.Order,
      Url = header.Url
    };

    public static List<CommonMenuItem> ToItems(this List<FoCommonMenuItem> items)
    {
      return items.Select(item => item.ToItem()).ToList();
    }

    public static CommonMenuItem ToItem(this FoCommonMenuItem item) => new CommonMenuItem()
    {
      Description = item.Description,
      DisplayName = item.DisplayName,
      Order = item.Order,
      Url = item.Url,
      ImageContent = item.ImageContent,
      ItemId = item.ItemId,
      SectionHeader = item.SectionHeader
    };
  }
}

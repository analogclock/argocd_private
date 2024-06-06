using System.Collections.Generic;
using System.Linq;
using FinsProvisioning.Models;

namespace FinsProvisioning.Helpers
{
  public static class MenuExtensions
  {
    public static List<ExpandedCommonItem> GetUserMenu(this Menu menu, FullUserDetails single)
    {
      var userMenu = single.UserMenu.Where(x => x.Visibility.ToLowerInvariant() != "hide");
      var list = new List<ExpandedCommonItem>();
      foreach (var item in menu.UserMenuItems)
      {
        var findMe = userMenu.FirstOrDefault(x => x.Id == item.ItemId);
        if (findMe != null)
        {
          var men = new ExpandedCommonItem()
          {
            Visibility = findMe.Visibility,
            Description = item.Description,
            DisplayName = item.DisplayName,
            ImageContent = item.ImageContent,
            ItemId = item.ItemId,
            Order = item.Order,
            Url = item.Url
          };
          list.Add(men);
        }
      }

      return list;
    }

    public static List<ExpandedSupportHeader> GetSupportMenu(this Menu menu, FullUserDetails single)
    {
      var sHeaders = new List<ExpandedSupportHeader>();

      // remove hidden ones
      var supportMenu = single.SupportMenu.Where(x => x.Visibility.ToLowerInvariant() != "hide");
      var groupThem = menu.SupportMenuItems.GroupBy(x => x.SectionHeader);
      foreach (var menuHeader in menu.SupportMenuHeaders)
      {
        var header = new ExpandedSupportHeader()
        {
          Description = menuHeader.Description,
          DisplayName = menuHeader.DisplayName,
          Order = menuHeader.Order,
          Url = menuHeader.Url,
          Items = new List<ExpandedCommonItem>()
        };

        var grouper = groupThem.FirstOrDefault(x => x.Key == menuHeader.DisplayName);

        if (grouper != null)
        {
          // now loop the innards
          var list = new List<ExpandedCommonItem>();
          foreach (var item in grouper)
          {
            var findMe = supportMenu.FirstOrDefault(x => x.Id == item.ItemId);
            if (findMe != null)
            {
              var men = new ExpandedCommonItem()
              {
                Visibility = findMe.Visibility,
                Description = item.Description,
                DisplayName = item.DisplayName,
                ImageContent = item.ImageContent,
                ItemId = item.ItemId,
                Order = item.Order,
                Url = item.Url
              };
              list.Add(men);
            }
          }

          header.Items = list;
        }

        sHeaders.Add(header);
      }

      return sHeaders;
    }

    public static List<ExpandedPortalHeader> GetPortalMenu(this Menu menu, FullUserDetails single)
    {
      var sHeaders = new List<ExpandedPortalHeader>();

      // remove hidden ones
      var portalMenu = single.Portals.Where(x => x.Visibility.ToLowerInvariant() != "hide");
      var groupThem = menu.PortalMenuItems.GroupBy(x => x.SectionHeader);
      foreach (var group in groupThem)
      {
        var findHeader = menu.PortalMenuHeaders.FirstOrDefault(x => x.DisplayName == group.Key);
        if (findHeader != null)
        {
          var header = new ExpandedPortalHeader()
          {
            Description = findHeader.Description,
            DisplayName = findHeader.DisplayName,
            Order = findHeader.Order,
            Url = findHeader.Url
          };

          // now loop the innards
          var list = new List<ExpandedCommonPortalItem>();
          foreach (var item in group)
          {
            var findMe = portalMenu.FirstOrDefault(x => x.Id == item.ItemId);
            if (findMe != null)
            {
              var men = new ExpandedCommonPortalItem()
              {
                Visibility = findMe.Visibility,
                Description = item.Description,
                DisplayName = item.DisplayName,
                ImageContent = item.ImageContent,
                ItemId = item.ItemId,
                AppName = item.AppName,
                Order = item.Order,
                Url = item.Url,
                SectionHeader = item.SectionHeader
              };
              list.Add(men);
            }
          }

          header.Items = list;
          sHeaders.Add(header);
        }
      }

      return sHeaders;
    }
  }
}

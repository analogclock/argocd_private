using System.Collections.Generic;
using FinsProvisioning.Models;
using FortinetOne.Client.Model.Responses;

namespace FinsProvisioning.FoResponseExtensions
{
  public static class FoGetUserPermissionsResponseEx
  {
    public static List<FullUserDetails> ToUserDetails(this FoGetUserPermissionsResponse foLoginAccountsByEmailResponse)
    {
      var accounts = new List<FullUserDetails>();
      foreach (var foLoginAccount in foLoginAccountsByEmailResponse.Data)
      {
        var portal = foLoginAccount.ToUserDetail();
        accounts.Add(portal);
      }

      return accounts;
    }

    public static FullUserDetails ToUserDetail(this FoGetUserPermissionsResponseData account)
    {
      if (account == null)
        return null;

      return new FullUserDetails()
      {
        AccountId = account.AccountId.Value,
        AccountCompany = account.AccountCompany,
        AccountEmail = account.AccountEmail,
        UserId = account.UserId.Value,
        MasterUserName = account.MasterUserName,
        UserEmail = account.UserEmail,
        AllAssetsAccess = account.AllAssestsAccess.Value,
        IamAccountName = account.IAMAccountName,
        IamUserName = account.IAMUserName,
        IsMasterUser = account.IsMasterUser.Value,
        UserAuthenticationPassed = account.UserAuthPassed.Value,
        UserAuthenticationUrl = account.UserAuthUrl,
        UserGroup = account.UserGroup,
        Portals = account.Portals.ToPortalItems(),
        UserMenu = account.UserMenu.ToMenuItems(),
        SupportMenu = account.SupportMenu.ToMenuItems()
      };
    }

    public static List<PortalItem> ToPortalItems(this List<FoPortalPermission> portals)
    {
      var tmpPortals = new List<PortalItem>();

      if (portals == null)
        return tmpPortals;

      foreach (var accountPortal in portals)
      {
        var userPortal = accountPortal.ToPortalItem();
        tmpPortals.Add(userPortal);
      }

      return tmpPortals;
    }

    public static PortalItem ToPortalItem(this FoPortalPermission portal)
    {
      return new PortalItem()
      {
        Id = portal.AppId.Value,
        AppName = portal.AppName,
        IsAllowAccess = portal.IsAllowAccess.Value,
        UserRole = portal.UserRole,
        Visibility = portal.Visibility
      };
    }

    public static List<MenuItem> ToMenuItems(this List<FoUserMenu> portals)
    {
      var tmpPortals = new List<MenuItem>();

      if (portals == null)
        return tmpPortals;

      foreach (var item in portals)
      {
        var userPortal = item.ToMenuItem();
        tmpPortals.Add(userPortal);
      }

      return tmpPortals;
    }

    public static MenuItem ToMenuItem(this FoUserMenu item)
    {
      return new MenuItem()
      {
        Id = item.ItemId,
        Visibility = item.Visibility
      };
    }
  }
}

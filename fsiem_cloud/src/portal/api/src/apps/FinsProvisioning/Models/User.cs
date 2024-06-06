using System.Collections.Generic;

namespace FinsProvisioning.Models
{
  public class User
  {
    public FullUserDetails Details { get; set; }

    public string Logo { get; set; }

    public List<ExpandedCommonItem> UserMenu { get; set; }

    public List<ExpandedPortalHeader> ServiceMenu { get; set; }

    public List<ExpandedSupportHeader> SupportMenu { get; set; }

    public User()
    { }

    public User(FullUserDetails user, string logo,
        List<ExpandedCommonItem> userMenu,
        List<ExpandedSupportHeader> supportMenu,
        List<ExpandedPortalHeader> serviceMenu)
    {
      Details = user;
      Logo = logo;
      UserMenu = userMenu;
      SupportMenu = supportMenu;
      ServiceMenu = serviceMenu;

      // remove these from the user details
      user.Portals = null;
      user.SupportMenu = null;
      user.UserMenu = null;
    }
  }

  public class ExpandedCommonItem : CommonMenuItem
  {
    public string Visibility { get; set; }
  }

  public class ExpandedSupportHeader : CommonHeaders
  {
    public List<ExpandedCommonItem> Items { get; set; }
  }

  public class ExpandedPortalHeader : CommonHeaders
  {
    public List<ExpandedCommonPortalItem> Items { get; set; }
  }

  public class ExpandedCommonPortalItem : CommonPortalItem
  {
    public string Visibility { get; set; }
  }
}

using System.Collections.Generic;

namespace FinsProvisioning.Models
{
  /// <summary>
  /// Smaller UserDetails object to handle some of the settings
  /// </summary>
  public class UserDetails
  {
    /// <summary>
    /// Account a user is associated with
    /// </summary>
    public int AccountId { get; set; }

    /// <summary>
    /// Account email a user is associated with
    /// </summary>
    public string AccountEmail { get; set; }

    /// <summary>
    /// Company a user is associated with
    /// </summary>
    public string AccountCompany { get; set; }

    /// <summary>
    /// User id of the given user
    /// </summary>
    public int UserId { get; set; }

    /// <summary>
    /// Email of the given user
    /// </summary>
    public string UserEmail { get; set; }

    /// <summary>
    /// Whether this account is a master account
    /// </summary>
    public bool IsMasterUser { get; set; }

    /// <summary>
    /// Master user name associated with this user
    /// </summary>
    public string MasterUserName { get; set; }

    /// <summary>
    /// IAM User Name of the given account
    /// </summary>
    public string IamUserName { get; set; }

    /// <summary>
    /// IAM Account Name of the given account
    /// </summary>
    public string IamAccountName { get; set; }

    public UserDetails()
    { }

    public UserDetails(FullUserDetails user)
    {
      AccountId = user.AccountId;
      AccountCompany = user.AccountCompany;
      AccountEmail = user.AccountEmail;
      UserId = user.UserId;
      UserEmail = user.UserEmail;
      IsMasterUser = user.IsMasterUser;
      MasterUserName = user.MasterUserName;
      IamUserName = user.IamUserName;
      IamAccountName = user.IamAccountName;
    }
  }

  /// <summary>
  /// Given user information
  /// </summary>
  public class FullUserDetails : UserDetails
  {
    /// <summary>
    /// Group information of the User
    /// </summary>
    public string UserGroup { get; set; }

    /// <summary>
    /// Does this account have access to all assets
    /// </summary>
    public bool AllAssetsAccess { get; set; }

    /// <summary>
    /// Has this user passed authentication
    /// </summary>
    public bool UserAuthenticationPassed { get; set; }

    /// <summary>
    /// where should the user be redirected to
    /// </summary>
    public string UserAuthenticationUrl { get; set; }

    /// <summary>
    /// A given set of portals associated with this user
    /// </summary>
    public List<PortalItem> Portals { get; set; }

    /// <summary>
    /// A given set of menu items associated with this user
    /// </summary>
    public List<MenuItem> UserMenu { get; set; }

    /// <summary>
    /// A given set of support items associated with this user
    /// </summary>
    public List<MenuItem> SupportMenu { get; set; }

    /// <summary>
    /// The email to display in the menu banner
    /// </summary>
    public string DisplayEmail
    {
      get
      {
        // we have a master user - so we should display the master email
        if (IsMasterUser || UserId == 0 || UserId == -1 || string.IsNullOrWhiteSpace(UserEmail))
          return AccountEmail;

        // we have an IAM account that we should display
        // the username format
        if (!string.IsNullOrWhiteSpace(IamUserName))
          return IamUserName;

        // we have a sub user
        return UserEmail;
      }
    }

    public FullUserDetails()
    {
      Portals = new List<PortalItem>();
      UserMenu = new List<MenuItem>();
      SupportMenu = new List<MenuItem>();
    }
  }

  /// <summary>
  /// Used to determine user portal access
  /// </summary>
  public class PortalItem
  {
    public int Id { get; set; }
    /// <summary>
    /// Application name of the portal
    /// </summary>
    public string AppName { get; set; }

    /// <summary>
    /// Users role who can access a portal
    /// </summary>
    public string UserRole { get; set; }

    /// <summary>
    /// Whether or not this particular user is allowed access to the given portal
    /// </summary>
    public bool IsAllowAccess { get; set; }

    /// <summary>
    /// Visibility of the Portal Item
    /// </summary>
    public string Visibility { get; set; }
  }

  /// <summary>
  /// Used to determine user portal access
  /// </summary>
  public class MenuItem
  {
    /// <summary>
    /// Item Id of the menu item
    /// </summary>
    public int Id { get; set; }

    /// <summary>
    /// Visibility of the menu item
    /// </summary>
    public string Visibility { get; set; }
  }
}

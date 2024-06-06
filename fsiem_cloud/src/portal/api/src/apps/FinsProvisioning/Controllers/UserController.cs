using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;
using FinsProvisioning.FoResponseExtensions;
using FinsProvisioning.Helpers;
using FinsProvisioning.Models;
using FortinetOne.Client;
using FortinetOne.Client.Model;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;

namespace FinsProvisioning.Controllers
{
  /// <summary>
  /// Accessing information about particular users
  /// </summary>
  [Authorize]
  [ApiController]
  [Route("api/[controller]")]
  public class UserController : ControllerBase
  {
    private readonly IFoClient _foClient;
    private readonly IUserManager _userManager;
    private readonly IMenuCache _menuCache;
    private readonly ILogger<UserController> _logger;

    public UserController(IFoClient foClient, IUserManager userManager,
        IMenuCache menuCache,
        ILogger<UserController> logger)
    {
      _foClient = foClient ?? throw new ArgumentNullException(nameof(foClient));
      _userManager = userManager ?? throw new ArgumentNullException(nameof(userManager));
      _menuCache = menuCache;
      _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    /// <summary>
    /// Validate authentication token
    /// </summary>
    /// <response code ="200">Authentication is valid</response>
    /// <response code ="401">Authentication is invalid</response>
    [HttpHead]
    public IActionResult Head()
    {
      _logger.LogInformation("Authentication checked");
      return Ok();
    }

    /// <summary>
    /// Get all accounts associated with the Authentication tokens id
    /// </summary>
    /// <returns>All the accounts which are associated with the underlying token</returns>
    [HttpGet]
    public async Task<List<UserDetails>> Users()
    {
      var allUsers = await RetrieveAllUsers();

      var users = new List<UserDetails>();
      foreach (var user in allUsers)
      {
        var dto = new UserDetails(user);
        if (dto != null)
          users.Add(dto);
      }

      return users;
    }

    /// <summary>
    /// Get a single account associated with the authentication token plus their account id and user id
    /// </summary>
    /// <param name="accountId">account id associated with the user</param>
    /// <param name="userId">user id associated with the user</param>
    /// <returns>A single account for the given user + account id + user id</returns>
    /// <response code ="400">if the provided account id is null</response>
    [HttpGet]
    [Route("{accountId:int}/{userId:int?}")]
    [ProducesResponseType(400)]
    public async Task<ActionResult<User>> SingleUser(
      [Required, Range(0, int.MaxValue)] int accountId, int? userId)
    {
      var accounts = await RetrieveAllUsers();

      var hasAccount = accounts.Any(x => x.AccountId == accountId);

      if (!hasAccount)
      {
        _logger.LogInformation($"no account found for {accountId}");
        return Forbid();
      }

      // assume -1 if null, as this is a master user id
      var id = userId ?? -1;
      var single = accounts.FirstOrDefault(x => x.UserId == id);
      // we have our user menu - we need to grab the common data and merge them together
      // we also want to know which logo to show as well.

      // retrieve the common menu
      var menu = await _menuCache.GetAsync();

      // is this user a premium user?
      var logo = await _foClient.CommonService.GetFortiCloudLogoAsync(new FoSearchFilters()
      {
        AccountId = accountId
      });

      var whichLogo = menu.Logos.FirstOrDefault(x => x.LogoId == logo.Data.LogoId);

      var uMenu = menu.GetUserMenu(single);
      var sMenu = menu.GetSupportMenu(single);
      var pMenu = menu.GetPortalMenu(single);

      return new User(single, whichLogo.ImageContent, uMenu, sMenu, pMenu);
    }

    [NonAction]
    private async Task<List<FullUserDetails>> RetrieveAllUsers()
    {
      var fortinetIdentity = await _userManager.GetFortinetIdentityAsync();
      var userResponse = await _foClient.AuthService.GetUserPermissionsAsync(
          fortinetIdentity.GetAuthenticationAttributes()
      );

      return userResponse.ToUserDetails();
    }
  }
}

using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Amazon.CognitoIdentityProvider;
using Amazon.CognitoIdentityProvider.Model;
using FinsProvisioning.Models;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Http;
using Newtonsoft.Json;

namespace FinsProvisioning.Helpers
{
  public interface IUserManager
  {
    /// <summary>
    /// Retrieve user an fortinet identity from cognito
    /// </summary>
    /// <returns>Fortinet Identity for use with the API</returns>
    Task<FortinetIdentity> GetFortinetIdentityAsync();
  }

  public class UserManager : IUserManager
  {
    private readonly IHttpContextAccessor _httpContextAccessor;
    private readonly IAmazonCognitoIdentityProvider _cognito;
    public UserManager(IHttpContextAccessor httpContextAccessor, IAmazonCognitoIdentityProvider cognito)
    {
      _httpContextAccessor = httpContextAccessor;
      _cognito = cognito;

    }

    public async Task<FortinetIdentity> GetFortinetIdentityAsync()
    {
      var user = _httpContextAccessor.HttpContext.User;

      // retrieve the access token from the HttpContext
      // NOTE: You must set SaveToken to true to allow for access here
      var accessToken = await _httpContextAccessor.HttpContext.GetTokenAsync("FortinetOne", "access_token");

      // get the user info from cognito
      var userCognito = await _cognito.GetUserAsync(new GetUserRequest()
      {
        AccessToken = accessToken
      });

      // retrieve our user information
      var identity = userCognito.UserAttributes.Find(x => x.Name == "identities");
      var authStatus = userCognito.UserAttributes.Find(x => x.Name == "custom:auth_status");
      var iamAccountName = userCognito.UserAttributes.Find(x => x.Name == "custom:IAM_account_name");
      var iamAccountAlias = userCognito.UserAttributes.Find(x => x.Name == "custom:IAM_account_alias");
      var iamUserName = userCognito.UserAttributes.Find(x => x.Name == "custom:IAM_username");

      // we have initially got a list of identities
      var identities = JsonConvert.DeserializeObject<List<FortinetIdentity>>(identity.Value);

      // we just want the first one
      var fortinetIdentity = identities.FirstOrDefault();

      // this should really never be null, but just incase we set it to null
      fortinetIdentity.AuthStatus = authStatus?.Value ?? null;
      fortinetIdentity.IAMAccountName = iamAccountName?.Value ?? null;
      fortinetIdentity.IAMAccountAlias = iamAccountAlias?.Value ?? null;
      fortinetIdentity.IAMUsername = iamUserName?.Value ?? null;
      return fortinetIdentity;
    }
  }
}

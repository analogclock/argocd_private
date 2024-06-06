using System.Collections.Generic;
using FortinetOne.Client.Model;
using Newtonsoft.Json;

namespace FinsProvisioning.Models
{
  /// <summary>
  /// A representation of a Fortinet Identity
  /// </summary>
  public class FortinetIdentity
  {
    /// <summary>
    /// Private backed for UserId, this allows us to add the @fortinet.com domain when we
    /// are using LDAP credentials - this is because in production FAC does not return the @fortinet.com
    /// for internal users
    /// </summary>
    private string _userId;
    /// <summary>
    /// User id from the authentication token === email
    /// </summary>
    [JsonProperty("userId")]
    public string UserId
    {
      get => _userId;
      set => _userId = !value.Contains("@") ? $"{value}@fortinet.com" : value;
    }

    /// <summary>
    /// Strip out any forbidden chars from the user whilst we are using
    /// it to tie TMP entitlements
    /// </summary>
    public string SafeUser => UserId.Replace("@", "-").Replace(".", "-");

    /// <summary>
    /// The provider of the authentication token
    /// </summary>
    [JsonProperty("providerName")]
    public string ProviderName { get; set; }

    /// <summary>
    /// The type of provider
    /// </summary>
    [JsonProperty("providerType")]
    public string ProviderType { get; set; }

    /// <summary>
    /// The issuer of the authentication token
    /// </summary>
    [JsonProperty("issuer")]
    public string Issuer { get; set; }

    /// <summary>
    /// Where this was a primary token
    /// </summary>
    [JsonProperty("primary")]
    public bool Primary { get; set; }

    /// <summary>
    /// When this token was created
    /// </summary>
    [JsonProperty("dateCreated")]
    public string DateCreated { get; set; }

    /// <summary>
    /// Authentication status of the user
    /// </summary>
    public string AuthStatus { get; set; }

    /// <summary>
    /// Account name associated with the user
    /// </summary>
    public string IAMAccountName { get; set; }

    /// <summary>
    /// Account Alias associated with the user
    /// </summary>
    public string IAMAccountAlias { get; set; }

    /// <summary>
    /// Username associated with the user
    /// </summary>
    public string IAMUsername { get; set; }

    /// <summary>
    /// Retrieve a set of Authentication attributes to use for User Permission
    /// requests.
    /// </summary>
    /// <returns></returns>
    public List<AuthAttribute> GetAuthenticationAttributes()
    {
      var authAttributes = new List<AuthAttribute>()
            {
                new AuthAttribute("NameID", UserId),
                new AuthAttribute("Authentication_status", AuthStatus)
            };

      // the following add the authentication attributes needed to process a User Permission request
      if (!string.IsNullOrWhiteSpace(IAMAccountName))
        authAttributes.Add(new AuthAttribute("IAM_account_name", IAMAccountName));

      if (!string.IsNullOrWhiteSpace(IAMAccountAlias))
        authAttributes.Add(new AuthAttribute("IAM_account_alias", IAMAccountAlias));

      if (!string.IsNullOrWhiteSpace(IAMUsername))
        authAttributes.Add(new AuthAttribute("IAM_username", IAMUsername));

      return authAttributes;
    }
  }
}

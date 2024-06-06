using System.Collections.Generic;
using Newtonsoft.Json;

namespace FortinetOne.Client.Model
{
  public class SecurityCategory
  {
    public const string SsoPortal = "Security.SSO.Portal";
  }

  public class ResultSet
  {
    public const string TimestampOnly = "TimeStampOnly";
  }

  public class FoSearchFilters : FoRequestData
  {
    // absolutely weird quirk of FortiCloud API - some are snake, some are Camel ;-)
    [JsonProperty(PropertyName = "accountId", NullValueHandling = NullValueHandling.Ignore)]
    public int? AnAccountId { get; set; } = null;

    [JsonProperty(PropertyName = "account_id", NullValueHandling = NullValueHandling.Ignore)]
    public int? AccountId { get; set; } = null;

    [JsonProperty(PropertyName = "user_id", NullValueHandling = NullValueHandling.Ignore)]
    public int? UserId { get; set; } = null;

    [JsonProperty(PropertyName = "product_snmask", NullValueHandling = NullValueHandling.Ignore)]
    public string ProductSnMask { get; set; }

    [JsonProperty(PropertyName = "support_types", NullValueHandling = NullValueHandling.Ignore)]
    public string SupportType { get; set; }

    [JsonProperty(PropertyName = "serial_number", NullValueHandling = NullValueHandling.Ignore)]
    public string SerialNumber { get; set; }

    [JsonProperty(PropertyName = "uuid", NullValueHandling = NullValueHandling.Ignore)]
    public string Uuid { get; set; }

    [JsonProperty(PropertyName = "serial_numbers", NullValueHandling = NullValueHandling.Ignore)]
    public List<string> SerialNumbers { get; set; } = null;

    [JsonProperty(PropertyName = "email", NullValueHandling = NullValueHandling.Ignore)]
    public string Email { get; set; }

    [JsonProperty(PropertyName = "account_email", NullValueHandling = NullValueHandling.Ignore)]
    public string AccountEmail { get; set; }

    [JsonProperty(PropertyName = "category", NullValueHandling = NullValueHandling.Ignore)]
    public string Category { get; set; }

    [JsonProperty(PropertyName = "resultset", NullValueHandling = NullValueHandling.Ignore)]
    public string ResultSet { get; set; }

    [JsonProperty(PropertyName = "access_token", NullValueHandling = NullValueHandling.Ignore)]
    public string AccessToken { get; set; }

    [JsonProperty(PropertyName = "user_email", NullValueHandling = NullValueHandling.Ignore)]
    public string UserEmail { get; set; }

    [JsonProperty(PropertyName = "iam_account_name", NullValueHandling = NullValueHandling.Ignore)]
    public string IAMAccountName { get; set; }

    [JsonProperty(PropertyName = "iam_user_name", NullValueHandling = NullValueHandling.Ignore)]
    public string IAMUserName { get; set; }

    // Absolutely hideous way to handle authentication and permissions request
    // this is because FCloud wants all the auth attributes returned from saml in 
    // a simple digestable list
    [JsonProperty(PropertyName = "auth_attributes", NullValueHandling = NullValueHandling.Ignore)]
    public List<AuthAttribute> AuthAttributes { get; set; } = null;

    public FoSearchFilters()
    {
    }
  }

  // Defines a very specific class for this instead of using
  // Key value pairs as we need to control the JSON property naming
  public class AuthAttribute
  {
    [JsonProperty(PropertyName = "name", NullValueHandling = NullValueHandling.Ignore)]
    public string Name { get; set; } = null;

    [JsonProperty(PropertyName = "value", NullValueHandling = NullValueHandling.Ignore)]
    public string Value { get; set; } = null;

    public AuthAttribute()
    { }

    public AuthAttribute(string name, string value)
    {
      Name = name;
      Value = value;
    }
  }
}

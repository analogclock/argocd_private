using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using Amazon;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace FinsProvisioning.Models
{
  public class AlternateCertificate
  {
    public string Body { get; set; }
    public string Private { get; set; }
    public string Chain { get; set; }
  }

  public enum SupportedDeploymentType
  {
    Enterprise,
    ServiceProvider
  }

  public static class DeploymentTypeExtensions
  {
    private static readonly Dictionary<SupportedDeploymentType, string> _deploymentType = new Dictionary<SupportedDeploymentType, string>
        {
            { SupportedDeploymentType.ServiceProvider, "sp"},
            { SupportedDeploymentType.Enterprise, "va"}
        };

    public static string ToDeploymentType(this SupportedDeploymentType deploymentType)
    {
      if (_deploymentType.ContainsKey(deploymentType))
      {
        return _deploymentType[deploymentType];
      }

      throw new NotSupportedException($"provided value is not supported: {deploymentType}");
    }

    public static SupportedDeploymentType ToSupportedDeploymentType(string supported)
    {
      if (_deploymentType.ContainsValue(supported))
      {
        return _deploymentType.First(x => x.Value == supported).Key;
      }

      throw new NotSupportedException($"provided value is not supported: {supported}");
    }
  }

  /// <summary>
  /// Shim enum - used to map the regions we support
  /// as an input to Request
  /// </summary>
  public enum SupportedRegion
  {
    EUCentral1, // Frankfurt
    EUWest1, // Ireland
    EUWest2, // London
    EUWest3, // Paris
    EUNorth1, // Stockholm
    USEast1, // N.Virginia
    USEast2, // Ohio
    USWest1, // N.California
    USWest2, // Oregon
    APNortheast1, // Tokyo
    APNortheast2, // Seoul
    APSoutheast1, // Singapore
    APSoutheast2, // Sydney
    APSouth1, // Mumbai
    CACentral1, // Canada
    MESouth1, // Bahrain
    APEast1, // Hong Kong
    AFSouth1, // Cape Town
  }

  public static class SupportedRegionEx
  {
    /// <summary>
    /// Map our supported region to aws region endpoint
    /// Note: RegionEndpoint is not an enum - it is a const
    /// It may look like an enum, but it isn't so we cannot use it in a
    /// request
    /// </summary>
    private static readonly Dictionary<SupportedRegion, RegionEndpoint> _supportedToRegion = new Dictionary<SupportedRegion, RegionEndpoint>
        {
            { SupportedRegion.EUCentral1, RegionEndpoint.EUCentral1},
            { SupportedRegion.EUWest1, RegionEndpoint.EUWest1},
            { SupportedRegion.EUWest2, RegionEndpoint.EUWest2},
            { SupportedRegion.EUWest3, RegionEndpoint.EUWest3},
            { SupportedRegion.EUNorth1, RegionEndpoint.EUNorth1},
            { SupportedRegion.USEast1, RegionEndpoint.USEast1},
            { SupportedRegion.USEast2, RegionEndpoint.USEast2},
            { SupportedRegion.USWest1, RegionEndpoint.USWest1},
            { SupportedRegion.USWest2, RegionEndpoint.USWest2},
            { SupportedRegion.APNortheast1, RegionEndpoint.APNortheast1},
            { SupportedRegion.APNortheast2, RegionEndpoint.APNortheast2},
            { SupportedRegion.APSoutheast1, RegionEndpoint.APSoutheast1},
            { SupportedRegion.APSoutheast2, RegionEndpoint.APSoutheast2},
            { SupportedRegion.APSouth1, RegionEndpoint.APSouth1},
            { SupportedRegion.CACentral1, RegionEndpoint.CACentral1},
            { SupportedRegion.MESouth1, RegionEndpoint.MESouth1},
            { SupportedRegion.APEast1, RegionEndpoint.APEast1},
            { SupportedRegion.AFSouth1, RegionEndpoint.AFSouth1},
        };

    /// <summary>
    /// Transpose SupportedRegion to a supported RegionEndpoint
    /// </summary>
    /// <param name="supported">FIN Supported Region</param>
    /// <returns>AWS RegionEndpoint</returns>
    public static RegionEndpoint ToRegion(this SupportedRegion supported)
    {
      if (_supportedToRegion.ContainsKey(supported))
      {
        return _supportedToRegion[supported];
      }

      throw new NotSupportedException($"provided value is not supported: {supported}");
    }

    /// <summary>
    /// Transpose RegionEndpoint into SupportedRegion
    /// </summary>
    /// <param name="region">AWS RegionEndpoint</param>
    /// <returns>FIN Supported Region</returns>
    public static SupportedRegion ToSupportedRegion(this RegionEndpoint region)
    {
      if (_supportedToRegion.ContainsValue(region))
      {
        return _supportedToRegion.First(x => x.Value == region).Key;
      }

      throw new NotSupportedException($"provided value is not supported: {region}");
    }
  }

  /// <summary>
  /// User information required to activate a stack
  /// </summary>
  public class ActivatedStackInformation
  {
    /// <summary>
    /// rules of the password game are:
    /// 1. between 8 - 64
    /// 2. at least one upper case char
    /// 3. at least one lower case char
    /// 4. at least one number
    /// 5. at least one special char (using \W + _ regex)
    /// </summary>
    private readonly Regex _passwordRegex = new(@"^(?=(.*[a-z].*){1,})(?=(.*[A-Z].*){1,})(?=.*\d.*)(?=.*[\W|_].*)[a-zA-Z0-9\S]{8,64}$");

    /// <summary>
    /// The deployer admin username for the FortiSIEM stack
    /// </summary>
    public string AdminUsername { get; set; } = "Admin";

    /// <summary>
    /// The deployer admin password for the FortiSIEM stack
    /// </summary>
    public string AdminPassword { get; set; }

    [JsonConverter(typeof(StringEnumConverter))]
    public SupportedDeploymentType? DeploymentType { get; set; }

    /// <summary>
    /// AWS region that a stack will be deplayed into
    /// </summary>
    [JsonConverter(typeof(StringEnumConverter))]
    public SupportedRegion? Region { get; set; }

    public string Ipv4CIDRList { get; set; }
    public string Ipv6CIDRList { get; set; }

    public string AdditionalContacts { get; set; }

    public string AlternateDomain { get; set; }
    public AlternateCertificate Certificate { get; set; } = null;

    public string ExternalStorageDest { get; set; } = null;

    /// <summary>
    /// Control whether the deployment should recheck
    /// and apply latest SKU values
    /// </summary>
    public bool ShouldUpdateSKU { get; set; } = false;

    public ProductSKU DeploymentSKU { get; set; } = null;

    public string StorageType { get; set; } = "";

    /// <summary>
    /// AWS Region Endpoint to use
    /// Defaults to EUWest1
    /// </summary>
    public RegionEndpoint RegionEndpoint
    {
      get
      {
        if (Region.HasValue)
          return Region.Value.ToRegion();

        return SupportedRegion.EUWest1.ToRegion();
      }
    }

    /// <summary>
    /// What type of deployment will be deployed for the license
    /// Enterprise == va
    /// ServiceProvider == sp
    /// </summary>
    public string DeploymentTypeString
    {
      get
      {
        if (DeploymentType.HasValue)
          return DeploymentType.Value.ToDeploymentType();

        return SupportedDeploymentType.Enterprise.ToDeploymentType();
      }
    }

    /// <summary>
    /// Is the admin password provided valid
    /// Rules of the game:
    ///
    /// </summary>
    public bool IsValidPassword
    {
      get
      {
        // we aren't valid if we are empty
        if (string.IsNullOrWhiteSpace(AdminPassword))
          return false;

        // check if we are valid with the regex
        if (!_passwordRegex.IsMatch(AdminPassword))
          return false;

        return true;
      }
    }
  }
}

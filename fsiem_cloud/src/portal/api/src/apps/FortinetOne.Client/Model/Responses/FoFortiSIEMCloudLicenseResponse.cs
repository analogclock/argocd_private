using Newtonsoft.Json;

namespace FortinetOne.Client.Model.Responses
{
  public class FoFortiSIEMCloudLicenseResponse : FoResponseV3<FoFortiSIEMCloudLicenseData>
  {
  }

  public class FoFortiSIEMCloudLicenseData
  {
    // raw json returned by FortiCloud API
    //{
    //  "serialNumber": "FSMCLD0000000112",
    //  "licenseKey": "base64EncodedString"
    //}

    [JsonProperty(PropertyName = "serialNumber")]
    public string SerialNumber { get; set; } = string.Empty;

    [JsonProperty(PropertyName = "licenseKey")]
    public string LicenseKey { get; set; } = string.Empty;

  }
}

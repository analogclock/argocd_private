using System;
using FinsProvisioning.Models;
using FortinetOne.Client.Model.Responses;

namespace FinsProvisioning.FoResponseExtensions
{
  public static class FoFortiSIEMCloudLicenseResponseEx
  {
    public static License ToLicense(this FoFortiSIEMCloudLicenseResponse response)
    {
      if (response == null)
        throw new ArgumentNullException(nameof(response));

      var lic = new License()
      {
        SerialNumber = response.Data.SerialNumber,
        LicenseKey = response.Data.LicenseKey
      };
      return lic;
    }
  }
}

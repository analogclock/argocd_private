using System.Collections.Generic;
using System.Linq;
using FinsProvisioning.Models;
using FortinetOne.Client.Model.Responses;

namespace FinsProvisioning.FoResponseExtensions
{
  public static class FoFortiSIEMCloudResponseEx
  {
    private const int ComputeSupportCode = 224;
    private const int OnlineStorageCode = 225;
    private const int ArchiveStorageCode = 226;

    public static List<Deployment> ToDeployments(this FoFortiSIEMCloudResponse response)
    {
      var tmp = new List<Deployment>();
      if (response.Data == null)
        return tmp;

      var assets = response.Data;
      foreach (var asset in assets)
        tmp.Add(asset.ToStack());
      return tmp;
    }

    public static Deployment ToStack(this FoFortiSIEMCloudResponseData foAsset)
    {
      return new Deployment
      {
        Description = foAsset.Description,
        SerialNumber = foAsset.SerialNumber,
        Information = new Activate(),
        Entitlement = foAsset.Entitlements.ToProductSKU()
      };
    }

    public static ProductSKU ToProductSKU(this List<Term> terms)
    {
      var grouped = terms.ToLookup(x => x.SupportType);

      return new ProductSKU
      {
        Compute = grouped[ComputeSupportCode].ToFirstEntitlement(),
        OnlineStorage = grouped[OnlineStorageCode].ToFirstEntitlement(),
        ArchiveStorage = grouped[ArchiveStorageCode].ToFirstEntitlement()
      };
    }

    private static IndividualEntitlement ToFirstEntitlement(this IEnumerable<Term> terms)
    {
      return terms?.FirstOrDefault()?.ToEntitlement() ?? new IndividualEntitlement();
    }

    public static IndividualEntitlement ToEntitlement(this Term term)
    {
      return new IndividualEntitlement()
      {
        EndDate = term.EndDate,
        StartDate = term.StartDate,
        Quantity = term.Quantity
      };
    }
  }
}

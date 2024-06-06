using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using FortinetOne.Client.Model;
using FortinetOne.Client.Model.Responses;
using FortinetOne.Client.Utils;

namespace FortinetOne.Client.Services
{
  public interface IFoFortiSIEMCloudService
  {
    Task<FoFortiSIEMCloudResponse> GetProductEntitlementsAsync(int accountId);
    Task<FoFortiSIEMCloudResponse> GetProductEntitlementsAsync(string serialNumber);
    Task<FoFortiSIEMCloudResponse> GetProductEntitlementsAsync(List<string> serialNumber);
    Task<FoFortiSIEMCloudLicenseResponse> GetLicenseKeyAsync(string serialNumber, string uuid);
  }

  /// <summary>
  /// Use this service to query /FortinetOneProductService.asmx/Process
  /// </summary>
  public class FoFortiSIEMCloudService : IFoFortiSIEMCloudService
  {
#pragma warning disable IDE0052

    private readonly IFoClient _client;

    public FoFortiSIEMCloudService(IFoClient client)
    {
      _client = client ?? throw new ArgumentNullException(nameof(client));
    }

    public Task<FoFortiSIEMCloudResponse> GetProductEntitlementsAsync(int accountId)
    {
      var filters = new FoSearchFilters()
      {
        RelativePath = FoApiRelativePath.FortiSIEMCloudService,
        Type = FoRequestType.FortiSIEMCloudGetProductEntitlementsPayload,
        AccountId = accountId
      };

      return _client.PostRequestAsync<FoFortiSIEMCloudResponse>(filters);
    }

    public Task<FoFortiSIEMCloudResponse> GetProductEntitlementsAsync(string serialNumber)
    {
      return GetProductEntitlementsAsync(new List<string>() { serialNumber });
    }

    public Task<FoFortiSIEMCloudResponse> GetProductEntitlementsAsync(List<string> serialNumbers)
    {
      var filters = new FoSearchFilters()
      {
        RelativePath = FoApiRelativePath.FortiSIEMCloudService,
        Type = FoRequestType.FortiSIEMCloudGetProductEntitlementsBySerialNumberPayload,
        SerialNumbers = serialNumbers
      };

      return _client.PostRequestAsync<FoFortiSIEMCloudResponse>(filters);
    }

    public Task<FoFortiSIEMCloudLicenseResponse> GetLicenseKeyAsync(string serialNumber, string uuid)
    {
      var filters = new FoSearchFilters()
      {
        RelativePath = FoApiRelativePath.FortiSIEMCloudService,
        Type = FoRequestType.GetLicenseKeyPayload,
        Uuid = uuid,
        SerialNumber = serialNumber
      };

      return _client.PostRequestAsync<FoFortiSIEMCloudLicenseResponse>(filters);
    }
  }
}

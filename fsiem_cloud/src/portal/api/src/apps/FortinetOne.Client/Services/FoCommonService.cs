using System;
using System.Threading.Tasks;
using FortinetOne.Client.Model;
using FortinetOne.Client.Model.Responses;
using FortinetOne.Client.Utils;

namespace FortinetOne.Client.Services
{
  public interface IFoCommonService
  {
    /// <summary>
    /// Retrieve the list of supported portals for all FortiCloud Services
    /// </summary>
    /// <returns></returns>
    Task<FoPortalListResponseV3> GetPortalListAsync();
    Task<FoCommonDataResponse> GetCommonDataAsync();
    Task<FoCommonDataLastUpdateTimeResponse> GetCommonDataLastUpdateTimeAsync();

    Task<FoGetFortiCloudLogoResponse> GetFortiCloudLogoAsync(FoSearchFilters filters);

    Task<FoGetFortiCloudPremiumSubscriptionResponse> GetFortiCloudPremiumSubscriptionAsync(FoSearchFilters filters);

    Task<FoGetAccountsByEmailResponse> GetAccountsByEmailAsync(string email);

    Task<FoAccountDetailsV3Response> GetAccountDetailsAsync(FoSearchFilters filters);
  }

  /// <summary>
  /// Use this service to query /FortinetOneCommonService.asmx/Process
  /// </summary>
  public class FoCommonService : IFoCommonService
  {
    private readonly IFoClient _client;

    public FoCommonService(IFoClient client)
    {
      _client = client ?? throw new ArgumentNullException(nameof(client));
    }

    public Task<FoPortalListResponseV3> GetPortalListAsync()
    {
      var filters = new FoSearchFilters()
      {
        RelativePath = FoApiRelativePath.CommonV3,
        Type = FoRequestType.GetPortalListPayload
      };

      var resType = "result";
      return _client.PostRequestAsync<FoPortalListResponseV3>(filters, resType);
    }

    public Task<FoCommonDataResponse> GetCommonDataAsync()
    {
      var filters = new FoSearchFilters()
      {
        RelativePath = FoApiRelativePath.CommonV3,
        Type = FoRequestType.GetCommonDataPayload
      };

      return _client.PostRequestAsync<FoCommonDataResponse>(filters);
    }

    public Task<FoCommonDataLastUpdateTimeResponse> GetCommonDataLastUpdateTimeAsync()
    {
      var filters = new FoSearchFilters()
      {
        RelativePath = FoApiRelativePath.CommonV3,
        Type = FoRequestType.GetCommonDataLastUpdatePayload
      };

      return _client.PostRequestAsync<FoCommonDataLastUpdateTimeResponse>(filters);
    }

    public Task<FoGetFortiCloudLogoResponse> GetFortiCloudLogoAsync(FoSearchFilters filters)
    {
      filters.AddRelativePath(FoApiRelativePath.CommonV3);
      filters.AddRequestType(FoRequestType.GetFortiCloudLogoPayload);

      var resType = "result";
      return _client.PostRequestAsync<FoGetFortiCloudLogoResponse>(filters, resType);
    }

    public Task<FoGetFortiCloudPremiumSubscriptionResponse> GetFortiCloudPremiumSubscriptionAsync(FoSearchFilters filters)
    {
      filters.AddRelativePath(FoApiRelativePath.CommonV3);
      filters.AddRequestType(FoRequestType.GetFortiCloudPremiumSubscriptionPayload);

      return _client.PostRequestAsync<FoGetFortiCloudPremiumSubscriptionResponse>(filters);
    }

    public Task<FoGetAccountsByEmailResponse> GetAccountsByEmailAsync(string email)
    {
      var filters = new FoSearchFilters()
      {
        RelativePath = FoApiRelativePath.CommonV3,
        Type = FoRequestType.GetAccountsByEmailPayload,
        Email = email
      };

      return _client.PostRequestAsync<FoGetAccountsByEmailResponse>(filters);
    }

    public Task<FoAccountDetailsV3Response> GetAccountDetailsAsync(FoSearchFilters filters)
    {
      filters.AddRelativePath(FoApiRelativePath.CommonV3);
      filters.AddRequestType(FoRequestType.GetAccountDetailsPayload);

      return _client.PostRequestAsync<FoAccountDetailsV3Response>(filters);
    }
  }
}

using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using FortinetOne.Client.Model;
using FortinetOne.Client.Model.Responses;
using FortinetOne.Client.Utils;

namespace FortinetOne.Client.Services
{
  public interface IFoAuthService
  {
    Task<FoGetUserPermissionsResponse> GetUserPermissionsAsync(List<AuthAttribute> authAttributes);
    Task<FoGetAPIPermissionsResponse> GetAPIUserPermissionsAsync(FoSearchFilters filters);
  }

  /// <summary>
  /// Use this service to query /Common/FortinetOneAuthService.asmx/Process
  /// </summary>
  public class FoAuthService : IFoAuthService
  {
    private readonly IFoClient _client;

    public FoAuthService(IFoClient client)
    {
      _client = client ?? throw new ArgumentNullException(nameof(client));
    }

    public Task<FoGetAPIPermissionsResponse> GetAPIUserPermissionsAsync(FoSearchFilters filters)
    {
      // force these properties on to the object passed in
      filters.AddRelativePath(FoApiRelativePath.CommonAuthService);
      filters.AddRequestType(FoRequestType.GetAPIUserPermissionsPayload);

      var resType = "result";

      return _client.PostRequestAsync<FoGetAPIPermissionsResponse>(filters, resType);
    }

    public Task<FoGetUserPermissionsResponse> GetUserPermissionsAsync(List<AuthAttribute> authAttributes)
    {
      var filters = new FoSearchFilters()
      {
        RelativePath = FoApiRelativePath.CommonAuthService,
        Type = FoRequestType.GetUserPermissionsPayload
      };
      filters.AuthAttributes = authAttributes;

      var resType = "result";

      return _client.PostRequestAsync<FoGetUserPermissionsResponse>(filters, resType);
    }
  }
}

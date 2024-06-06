using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using FortinetOne.Client.Model;
using FortinetOne.Client.Model.Responses;
using FortinetOne.Client.Services;
using FortinetOne.Client.Utils;
using Newtonsoft.Json;

namespace FortinetOne.Client
{
  public interface IFoClient
  {
    IFoCommonService CommonService { get; }

    IFoFortiSIEMCloudService FortiSIEMCloudService { get; }

    IFoAuthService AuthService { get; }

    Task<T> PostRequestAsync<T>(FoSearchFilters filters, string resType = "result") where T : IFoResponse, new();
  }

  public class FoClient : HttpClient, IFoClient
  {
    public IFoCommonService CommonService { get; }

    public IFoFortiSIEMCloudService FortiSIEMCloudService { get; }

    public IFoAuthService AuthService { get; }

    /// <summary>
    /// Construct a new FoClient - note all SSL validation will be switched off.
    /// </summary>
    /// <param name="baseUrl">base fortinet one url to send requests to</param>
    /// <param name="handler"></param>
    public FoClient(string baseUrl, HttpMessageHandler handler) : base(handler)
    {
      if (string.IsNullOrEmpty(baseUrl))
        throw new ArgumentException("Value cannot be null or empty.", nameof(baseUrl));

      BaseAddress = new Uri(baseUrl, UriKind.Absolute);

      CommonService = new FoCommonService(this);
      FortiSIEMCloudService = new FoFortiSIEMCloudService(this);
      AuthService = new FoAuthService(this);
    }

    public async Task<T> PostRequestAsync<T>(FoSearchFilters filters, string resType = "result") where T : IFoResponse, new()
    {
      var req = new FoRequest
      {
        Data = filters
      };

      var url = BaseAddress.OriginalString.UriCombine(req.Data.RelativePath);
      var content = JsonConvert.SerializeObject(req, Formatting.Indented);
      var mediaType = "application/json";

      var stringContent = new StringContent(content, Encoding.Default, mediaType);

      var httpResp = await PostAsync(url, stringContent);

      var resp = new T { HttpResp = httpResp };
      resp.Parse(resType);
      return resp;
    }
  }
}

using System;
using System.Threading.Tasks;
using FinsProvisioning.FoResponseExtensions;
using FinsProvisioning.Models;
using FortinetOne.Client;

namespace FinsProvisioning.Helpers
{
  public interface IMenuCache
  {
    Task<Menu> GetAsync();
  }

  public class MenuCache : IMenuCache
  {
    private readonly IFoClient _foClient;

    public MenuCache(IFoClient foClient)
    {
      _foClient = foClient ?? throw new ArgumentNullException(nameof(foClient));
    }

    public async Task<Menu> GetAsync()
    {
      var menuResponse = await _foClient.CommonService.GetCommonDataAsync();
      return menuResponse.ToMenu();
    }
  }
}

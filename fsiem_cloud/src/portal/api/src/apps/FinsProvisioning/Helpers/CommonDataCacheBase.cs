using System;
using System.Threading.Tasks;
using FinsProvisioning.FoResponseExtensions;
using FinsProvisioning.Models;
using FortinetOne.Client;

namespace FinsProvisioning.Helpers
{
  public abstract class CommonDataCacheBase : IMenuCache
  {
    protected readonly IFoClient _foClient;

    protected CommonDataCacheBase(IFoClient foClient)
    {
      _foClient = foClient ?? throw new ArgumentNullException(nameof(foClient));
    }

    /// <summary>
    /// Retrieve the latest portal list
    /// This method will initialise the cache
    /// and check if there are any updates
    /// </summary>
    /// <returns>Latest list of portals</returns>
    public async Task<Menu> GetAsync()
    {
      // try to get the existing portals from the cache
      // this will return null on the first run through
      var menu = await GetPortalsFromCacheAsync();
      // we have the same time and the cache has something
      if (IsSyncLastUpdateEqual() && menu != null)
      {
        // get our initial list of portals - this also initiates the cache
        // and return them
        return menu;
      }

      // it is time to update our portal lists
      // go out and get the new ones from Fortinet One
      try
      {
        var commonData = await _foClient.CommonService.GetCommonDataAsync();
        menu = commonData.ToMenu();
      }
      catch // any exception that happens out of this call
      {
        // set the portals to an empty list
        menu = new Menu();
      }

      // reset the cache
      var newPortals = await SetPortalsInCacheAsync(menu);

      return newPortals;
    }

    protected abstract Task<Menu> GetPortalsFromCacheAsync();
    protected abstract bool IsSyncLastUpdateEqual();

    protected abstract Task<Menu> SetPortalsInCacheAsync(Menu portals);
  }
}

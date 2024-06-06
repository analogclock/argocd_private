using System;
using System.Threading.Tasks;
using FinsProvisioning.Models;
using FortinetOne.Client;

namespace FinsProvisioning.Helpers.Caches
{
  public class CommonDataPersistentCache : CommonDataCacheBase
  {
    private readonly ICommonDataCache _persistentCache;
    private readonly double _updateInSeconds;
    private Menu _menu;

    public CommonDataPersistentCache(IFoClient foClient, ICommonDataCache persistentCache, double updateInSeconds) : base(foClient)
    {
      _persistentCache = persistentCache;
      _updateInSeconds = updateInSeconds;
    }

    protected override async Task<Menu> GetPortalsFromCacheAsync()
    {
      // have we already got a memoize menu
      if (_menu != null)
        return _menu;

      _menu = await _persistentCache.GetAsync();

      // else we should get from the cache
      return _menu;
    }

    protected override bool IsSyncLastUpdateEqual()
    {
      var lastUpdated = _persistentCache.LastUpdate();
      if (lastUpdated.HasValue)
      {
        var lastUpdate = lastUpdated.Value;
        var now = DateTimeOffset.UtcNow;
        if ((now - lastUpdate).TotalSeconds < _updateInSeconds)
        {
          return true;
        }
      }

      return false;
    }

    protected override async Task<Menu> SetPortalsInCacheAsync(Menu portals)
    {
      var menu = await _persistentCache.CreateAsync(portals);
      if (menu)
      {
        _menu = portals;
        return _menu;
      }

      return null;
    }
  }
}

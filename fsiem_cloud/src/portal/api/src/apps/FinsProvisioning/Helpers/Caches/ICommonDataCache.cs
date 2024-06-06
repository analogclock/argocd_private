using System;
using System.Threading.Tasks;
using FinsProvisioning.Models;

namespace FinsProvisioning.Helpers.Caches
{
  public interface ICommonDataCache
  {
    bool Exists();
    Task<bool> CreateAsync(Menu portals);
    Task<Menu> GetAsync();
    DateTimeOffset? LastUpdate();
  }
}

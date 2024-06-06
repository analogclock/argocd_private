using System;
using System.IO;
using System.Threading.Tasks;
using FinsProvisioning.Models;
using Newtonsoft.Json;

namespace FinsProvisioning.Helpers.Caches
{
  public class FileBasedCommonDataCache : ICommonDataCache
  {
    private readonly string _location;
    public FileBasedCommonDataCache(string location)
    {
      _location = location;
    }

    public async Task<bool> CreateAsync(Menu portals)
    {
      try
      {
        var contents = JsonConvert.SerializeObject(portals, Formatting.Indented);
        await File.WriteAllTextAsync(_location, contents);
        return true;
      }
      catch
      {
        return false;
      }
    }

    public bool Exists()
    {
      return File.Exists(_location);
    }

    public async Task<Menu> GetAsync()
    {
      if (Exists())
      {
        var contents = await File.ReadAllTextAsync(_location);
        var portals = JsonConvert.DeserializeObject<Menu>(contents);
        return portals;
      }

      return null;
    }

    public DateTimeOffset? LastUpdate()
    {
      if (File.Exists(_location))
      {
        var fi = new FileInfo(_location);
        var lastUpdate = fi.LastWriteTimeUtc;
        return lastUpdate;
      }

      return null;
    }
  }
}

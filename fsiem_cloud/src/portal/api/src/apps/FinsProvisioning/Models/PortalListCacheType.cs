using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace FinsProvisioning.Models
{
  [JsonConverter(typeof(StringEnumConverter))]
  public enum PortalListCacheType
  {
    Memory,
    File,
    S3
  }
}

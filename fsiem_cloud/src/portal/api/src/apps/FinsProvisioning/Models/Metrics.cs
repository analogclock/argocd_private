using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace FinsProvisioning.Models
{
  [JsonConverter(typeof(StringEnumConverter))]
  public enum Metric
  {
    Events = 0,
    Status
  }
}

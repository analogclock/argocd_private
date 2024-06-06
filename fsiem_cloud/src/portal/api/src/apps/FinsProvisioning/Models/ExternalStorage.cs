using System;
using FinsProvisioning.Extensions;
using Newtonsoft.Json;

namespace FinsProvisioning.Models
{
  public class ExternalStorage
  {
    // Public readonly id so we can choose it on the UI should we need to
    public string Id => $"{SerialNumber}-{OrganizationId}";

    public string SerialNumber { get; set; }
    public int OrganizationId { get; set; }
    public string ExternalStorageDest { get; set; }
    public string LastStatus { get; set; } = null;

    // used to show the number of bytes transferred to the bucket
    public string DataTransferred { get; set; } = null;

    // any error or messages from successful
    public string Comments { get; set; } = null;

    [JsonConverter(typeof(AssumedUTCConverter))]
    public DateTimeOffset? LastUpdate { get; set; } = null;
  }
}

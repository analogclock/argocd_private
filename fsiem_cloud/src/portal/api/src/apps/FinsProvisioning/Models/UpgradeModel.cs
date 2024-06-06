using System;
using System.ComponentModel.DataAnnotations;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace FinsProvisioning.Models
{
  public enum UpgradeStatus
  {
    Pending,
    Complete,
    InProgress,
    Failed
  }

  public class UpgradeUpdateDTO
  {
    [Required]
    public string UpgradePath { get; set; }

    [Required]
    public DateTimeOffset ScheduledLocal { get; set; }

    [Required]
    public DateTimeOffset Scheduled { get; set; }
  }

  public class UpgradeModel : UpgradeUpdateDTO
  {
    // "serialNumber": {"S": "fsiem-mszymosz-1"},
    // "upgradePath": {"S": "6.4.0_6.5.0"},
    // local time selected by the user
    // "scheduledLocal": {"S": "2022-06-07T00:00:00-0800"},
    // this is the scheduled UTC time when it should run
    // "scheduled": {"S": "2022-06-07T08:00:00"},
    // "status": {"S": "Pending"}

    public UpgradeModel() { }

    public UpgradeModel(UpgradeUpdateDTO dto, string serialNumber, UpgradeStatus status)
    {
      SerialNumber = serialNumber;
      Status = status;
      UpgradePath = dto.UpgradePath;
      ScheduledLocal = dto.ScheduledLocal;
      Scheduled = dto.Scheduled;
    }

    public string SerialNumber { get; set; }

    [JsonConverter(typeof(StringEnumConverter))]
    public UpgradeStatus Status { get; set; }
  }
}

namespace FinsProvisioning.Models
{
  public class License
  {
    public string SerialNumber { get; set; } = string.Empty;
    public string LicenseKey { get; set; } = string.Empty;

    /// <summary>
    /// Shows if details of the entitlements associated with this license
    /// have changed from the last known entitlements.
    /// </summary>
    public bool HaveDetailsChanged { get; set; } = false;

    public ProductSKU Entitlement { get; set; } = null;
  }
}

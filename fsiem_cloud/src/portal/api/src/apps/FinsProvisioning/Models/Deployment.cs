using System;

namespace FinsProvisioning.Models
{
  public class ProductSKU
  {
    /// <summary>
    /// Compute entitlements which relates to the number of workers to deploy
    /// </summary>
    public IndividualEntitlement Compute { get; set; }

    /// <summary>
    /// Allowed online storage
    /// Quantity here is increments of 500GB (i.e if count == 2, then 1TB is provisioned)
    /// </summary>
    public IndividualEntitlement OnlineStorage { get; set; }

    /// <summary>
    /// Allowed archive storage
    /// Quantity here is increments of 500GB (i.e if count == 2, then 1TB is provisioned)
    /// </summary>
    public IndividualEntitlement ArchiveStorage { get; set; } = new IndividualEntitlement();

    /// <summary>
    /// Returns true if we have same compute, online and archive values
    /// (for the licensing purpose). We will only consider some properties in this comparison.
    /// </summary>
    /// <param name="other">Another instance of the class</param>
    /// <returns>True if objects are the same for the licensing purpose, otherwise false</returns>
    public bool IsSameForLicensingPurpose(ProductSKU other)
    {
      // they cannot be the same
      if (other == null)
        return false;

      return AreEntitlementsTheSame(Compute, other.Compute)
        && AreEntitlementsTheSame(OnlineStorage, other.OnlineStorage)
        && AreEntitlementsTheSame(ArchiveStorage, other.ArchiveStorage);
    }

    /// <summary>
    /// Check if the entire entitlement is valid or not
    /// </summary>
    /// <returns>
    /// true - entitlement is valid
    /// false - entitlement is not valid
    /// </returns>
    public bool IsValid()
    {
      // it is not valid to have no compute, or no online storage
      if (Compute == null || OnlineStorage == null)
        return false;

      // it is not valid for Compute or OnlineStorage to be nothing
      if (Compute.Quantity <= 0 || OnlineStorage.Quantity <= 0)
        return false;

      // check if each entitlement is valid or not
      // archive can be null in some scenarios
      return Compute.IsValid() &&
        OnlineStorage.IsValid() &&
        ArchiveStorage.IsValid(ArchiveStorage?.EndDate == null);
    }

    private static bool AreEntitlementsTheSame(IndividualEntitlement current, IndividualEntitlement other)
    {
      // they are the same
      if (current == null && other == null)
        return true;

      // not the same
      if (current == null && other != null)
        return false;

      if (current != null && other == null)
        return false;
      // some elements can be null, so make it first check nulls
      return current.IsSameForLicensingPurpose(other);
    }
  }

  /// <summary>
  /// What the particular serial number is entitled to, i.e the customer contract
  /// </summary>
  public class IndividualEntitlement
  {
    /// <summary>
    /// When this entitlement starts
    /// </summary>
    public DateTimeOffset? StartDate { get; set; } = null;

    /// <summary>
    /// When this entitlement ends
    /// </summary>
    public DateTimeOffset? EndDate { get; set; } = null;

    /// <summary>
    /// How many days are left for this deployment
    /// </summary>
    public int? ExpiryDays
    {
      get
      {
        // if we have neither start or end dates then we cannot
        // calculate how many days are left.
        if (EndDate == null)
          return null;

        // make ceiling the default here.
        return (int)Math.Ceiling((EndDate.Value - DateTimeOffset.UtcNow).TotalDays);
      }
    }

    /// <summary>
    /// Number of SKU units bought by the customer
    /// </summary>
    public int Quantity { get; set; } = 0;

    /// <summary>
    /// Returns true if expiry date and quantity are the same
    /// </summary>
    /// <param name="other">Another instance of the class</param>
    /// <returns>True if objects are the same for the licensing purpose, otherwise false</returns>
    public bool IsSameForLicensingPurpose(IndividualEntitlement other)
    {
      if (other == null)
        return false;

      return EndDate == other.EndDate &&
        Quantity == other.Quantity;
    }

    /// <summary>
    /// Is this entitlement valid or not
    /// </summary>
    /// <param name="canBeNull">If the expiry can be set to null then we need to tell it it can be</param>
    /// <returns>whether the entitlement is valid or not</returns>
    public bool IsValid(bool canBeNull = false)
    {
      if (!canBeNull && !ExpiryDays.HasValue)
        return false;

      if (canBeNull && !ExpiryDays.HasValue)
        return true;

      return ExpiryDays > 0 ? true : false;
    }
  }

  /// <summary>
  /// Specific Deployment information, such as location of the stack
  /// </summary>
  public class Information
  {
    /// <summary>
    /// Where the FortiSIEM Endpoint is located
    /// </summary>
    public string Url { get; set; }
  }

  /// <summary>
  /// Top level class to contain the entire deployment, plus its entitled info
  /// </summary>
  public class Deployment
  {
    /// <summary>
    /// Serial number for this deployment
    /// </summary>
    public string SerialNumber { get; set; }

    /// <summary>
    /// Description of the serial number provided by FortiCare
    /// </summary>
    public string Description { get; set; }

    public ProductSKU Entitlement { get; set; }

    public Activate Information { get; set; }

    public double TotalContractDays
    {
      get
      {
        if (Entitlement?.Compute == null)
          return 0;

        return (Entitlement.Compute.EndDate.Value - Entitlement.Compute.StartDate.Value).TotalDays;
      }
    }

    public bool IsEntitlementValid()
    {
      if (Entitlement == null)
        return false;

      return Entitlement.IsValid();
    }
  }
}

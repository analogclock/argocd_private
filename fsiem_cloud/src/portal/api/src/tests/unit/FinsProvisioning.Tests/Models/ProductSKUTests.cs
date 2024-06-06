using System;
using FinsProvisioning.Models;
using NUnit.Framework;

namespace FinsProvisioning.Tests.Models
{
  [TestFixture]
  public class ProductSKUTests
  {
    [Test]
    public void IsValid_NullCompute_NotValid()
    {
      var uut = new ProductSKU()
      {
        Compute = null,
        OnlineStorage = CreateEntitlement(),
        ArchiveStorage = CreateEntitlement()
      };
      Assert.That(!uut.IsValid());
    }

    [Test]
    public void IsValid_NullOnline_NotValid()
    {
      var uut = new ProductSKU()
      {
        Compute = CreateEntitlement(),
        OnlineStorage = null,
        ArchiveStorage = CreateEntitlement()
      };
      Assert.That(!uut.IsValid());
    }

    [Test]
    public void IsValid_ExpiredCompute_NotValid()
    {
      var uut = new ProductSKU()
      {
        Compute = CreateEntitlement(startDate: DateTimeOffset.UtcNow.AddDays(-21), endDate: DateTimeOffset.UtcNow.AddDays(-20)),
        OnlineStorage = null,
        ArchiveStorage = CreateEntitlement()
      };
      Assert.That(!uut.IsValid());
    }

    [Test]
    public void IsValid_ExpiredOnline_NotValid()
    {
      var uut = new ProductSKU()
      {
        Compute = CreateEntitlement(),
        OnlineStorage = CreateEntitlement(startDate: DateTimeOffset.UtcNow.AddDays(-21), endDate: DateTimeOffset.UtcNow.AddDays(-20)),
        ArchiveStorage = CreateEntitlement()
      };
      Assert.That(!uut.IsValid());
    }

    [Test]
    public void IsValid_AllCorrect_IsValid()
    {
      var uut = new ProductSKU()
      {
        Compute = CreateEntitlement(),
        OnlineStorage = CreateEntitlement(),
        ArchiveStorage = CreateEntitlement()
      };
      Assert.That(uut.IsValid());
    }

    [Test]
    public void IsValid_DefaultArchive_IsValid()
    {
      var uut = new ProductSKU()
      {
        Compute = CreateEntitlement(),
        OnlineStorage = CreateEntitlement(),
        ArchiveStorage = new IndividualEntitlement()
      };
      Assert.That(uut.IsValid());
    }

    [Test]
    public void IsValid_ArchiveWithInvalidValue_IsNotValid()
    {
      var uut = new ProductSKU()
      {
        Compute = CreateEntitlement(),
        OnlineStorage = CreateEntitlement(),
        ArchiveStorage = CreateEntitlement(startDate: DateTimeOffset.UtcNow.AddDays(-21), endDate: DateTimeOffset.UtcNow.AddDays(-20))
      };
      Assert.That(!uut.IsValid());
    }

    [Test]
    public void IsValid_ComputeWithNoQuantity_IsNotValid()
    {
      var uut = new ProductSKU()
      {
        Compute = CreateEntitlement(0),
        OnlineStorage = CreateEntitlement(),
        ArchiveStorage = CreateEntitlement()
      };
      Assert.That(!uut.IsValid());
    }

    [Test]
    public void IsValid_OnlineNoQuantity_IsNotValid()
    {
      var uut = new ProductSKU()
      {
        Compute = CreateEntitlement(),
        OnlineStorage = CreateEntitlement(0),
        ArchiveStorage = CreateEntitlement()
      };
      Assert.That(!uut.IsValid());
    }

    [Test]
    public void IsValid_ArchiveNoQuantity_IsValid()
    {
      var uut = new ProductSKU()
      {
        Compute = CreateEntitlement(),
        OnlineStorage = CreateEntitlement(),
        ArchiveStorage = CreateEntitlement(0)
      };
      Assert.That(uut.IsValid());
    }

    private static IndividualEntitlement CreateEntitlement(
      int? quantity = null,
      DateTimeOffset? startDate = null,
      DateTimeOffset? endDate = null)
    {
      return new IndividualEntitlement()
      {
        StartDate = startDate ?? DateTimeOffset.UtcNow.AddDays(-10),
        EndDate = endDate ?? DateTimeOffset.UtcNow.AddDays(10),
        Quantity = quantity ?? 10
      };

    }
  }
}

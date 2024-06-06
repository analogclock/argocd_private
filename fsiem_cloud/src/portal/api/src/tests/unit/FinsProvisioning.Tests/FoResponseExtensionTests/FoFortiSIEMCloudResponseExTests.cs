using System;
using System.Collections.Generic;
using FinsProvisioning.FoResponseExtensions;
using FortinetOne.Client.Model.Responses;
using NUnit.Framework;

namespace FinsProvisioning.Tests.FoResponseExtensionTests
{
  [TestFixture]
  public class FoFortiSIEMCloudResponseExTests
  {
    [Test]
    public void ToDeployments_NoArchiveNoOnline_ReturnsQuantityZero()
    {
      var resp = new FoFortiSIEMCloudResponse()
      {
        Data = new List<FoFortiSIEMCloudResponseData>()
        {
          new FoFortiSIEMCloudResponseData()
          {
            Entitlements = new List<Term>()
            {
              new Term()
              {
                SupportType = 224,
                Quantity = 1
              }
            }
          }
        }
      };

      var deployments = resp.ToDeployments();

      Assert.That(deployments != null);
      Assert.That(1 == deployments.Count);
      Assert.That(deployments[0].Entitlement.Compute != null);
      Assert.That(deployments[0].Entitlement.OnlineStorage != null);
      Assert.That(0 == deployments[0].Entitlement.OnlineStorage.Quantity);
      Assert.That(deployments[0].Entitlement.ArchiveStorage != null);
      Assert.That(0 == deployments[0].Entitlement.ArchiveStorage.Quantity);
    }

    [Test]
    public void ToDeployments_NoArchive_QuantityIsZero()
    {
      var resp = new FoFortiSIEMCloudResponse()
      {
        Data = new List<FoFortiSIEMCloudResponseData>()
        {
          new FoFortiSIEMCloudResponseData()
          {
            Entitlements = new List<Term>()
            {
              new Term()
              {
                SupportType = 224,
                Quantity = 1
              },
              new Term()
              {
                SupportType = 225,
                Quantity = 1
              }
            }
          }
        }
      };

      var deployments = resp.ToDeployments();

      Assert.That(deployments != null);
      Assert.That(1 == deployments.Count);
      Assert.That(deployments[0].Entitlement.Compute != null);
      Assert.That(deployments[0].Entitlement.OnlineStorage != null);
      Assert.That(deployments[0].Entitlement.ArchiveStorage != null);
      Assert.That(0 == deployments[0].Entitlement.ArchiveStorage.Quantity);
    }

    [Test]
    public void ToDeployments_WithArchive_Success()
    {
      var resp = new FoFortiSIEMCloudResponse()
      {
        Data = new List<FoFortiSIEMCloudResponseData>()
        {
          new FoFortiSIEMCloudResponseData()
          {
            Entitlements = new List<Term>()
            {
              new Term()
              {
                SupportType = 224,
                Quantity = 1
              },
              new Term()
              {
                SupportType = 225
              },
              new Term()
              {
                SupportType = 226
              }
            }
          }
        }
      };

      var deployments = resp.ToDeployments();

      Assert.That(deployments != null);
      Assert.That(1 == deployments.Count);
      Assert.That(deployments[0].Entitlement.Compute != null);
      Assert.That(deployments[0].Entitlement.OnlineStorage != null);
      Assert.That(deployments[0].Entitlement.ArchiveStorage != null);
    }

    [Test]
    public void ToDeployments_CheckQuantity_Success()
    {
      var resp = new FoFortiSIEMCloudResponse()
      {
        Data = new List<FoFortiSIEMCloudResponseData>()
        {
          new FoFortiSIEMCloudResponseData()
          {
            Entitlements = new List<Term>()
            {
              new Term()
              {
                SupportType = 224,
                Quantity = 1
              },
              new Term()
              {
                StartDate = DateTimeOffset.UtcNow.AddDays(-1),
                EndDate = DateTimeOffset.UtcNow.AddDays(1),
                SupportType = 225,
                Quantity = 1
              },
              new Term()
              {
                StartDate = DateTimeOffset.UtcNow.AddDays(-1),
                EndDate =  DateTimeOffset.UtcNow.AddDays(1),
                SupportType = 226,
                Quantity = 2
              }
            }
          }
        }
      };

      var deployments = resp.ToDeployments();

      Assert.That(deployments != null);
      Assert.That(1 == deployments.Count);
      Assert.That(deployments[0].Entitlement.Compute != null);
      Assert.That(deployments[0].Entitlement.OnlineStorage != null);
      Assert.That(deployments[0].Entitlement.ArchiveStorage != null);
      Assert.That(2 == deployments[0].Entitlement.ArchiveStorage.Quantity);
    }

    [Test]
    public void ToDeployments_ExpiryDays_IsWithinRange()
    {
      var resp = new FoFortiSIEMCloudResponse()
      {
        Data = new List<FoFortiSIEMCloudResponseData>()
        {
          new FoFortiSIEMCloudResponseData()
          {
            Entitlements = new List<Term>()
            {
              new Term()
              {
                EndDate = DateTimeOffset.UtcNow.AddDays(10),
                SupportType = 224,
                Quantity = 1
              },
              new Term()
              {
                StartDate = DateTimeOffset.UtcNow.AddDays(-1),
                EndDate = DateTimeOffset.UtcNow.AddDays(1),
                SupportType = 225
              },
              new Term()
              {
                StartDate = DateTimeOffset.UtcNow.AddDays(-1),
                EndDate =  DateTimeOffset.UtcNow.AddDays(1),
                SupportType = 226
              },
              new Term()
              {
                StartDate = DateTimeOffset.UtcNow.AddDays(2),
                EndDate =  DateTimeOffset.UtcNow.AddDays(2),
                SupportType = 226
              }
            }
          }
        }
      };

      var deployments = resp.ToDeployments();

      Assert.That(deployments != null);
      Assert.That(1 == deployments.Count);
      Assert.That(deployments[0].Entitlement.Compute != null);
      Assert.That(deployments[0].Entitlement.OnlineStorage != null);
      Assert.That(deployments[0].Entitlement.ArchiveStorage != null);

      Assert.That(1 == deployments[0].Entitlement.Compute.Quantity);
      Assert.That(10 == deployments[0].Entitlement.Compute.ExpiryDays);
    }
  }
}

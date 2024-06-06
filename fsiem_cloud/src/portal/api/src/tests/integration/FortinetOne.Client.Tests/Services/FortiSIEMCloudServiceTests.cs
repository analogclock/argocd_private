using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using NUnit.Framework;

namespace FortinetOne.Client.Tests.Services
{
  [TestFixture]
  internal class FortiSIEMCloudServiceTests
  {
    private FoClient _uut;

    [SetUp]
    public void SetUp()
    {
      var cert = CertificateUtilsExtensions.LoadTestCertificate();
      _uut = new FoClient(TestConsts.TestServer, new TestHttpHandler(cert));
    }

    [Test]
    public async Task GetProductEntitlementsAsync_WithValidAccount_ShouldNotBeNull()
    {
      var checkMe = 923180;
      var returned = await _uut.FortiSIEMCloudService.GetProductEntitlementsAsync(checkMe);

      await returned.AssertResponseAsync();
      Assert.That(returned.Data[0].SerialNumber != null);
      Assert.That(returned.Data[0].SerialNumber.StartsWith("FSMCLD"));

      Assert.Pass(await returned.PrintResponseAsync());
    }

    [Test]
    public async Task GetProductEntitlementsAsync_WithValidAccount_ShouldHaveCorrectEntitlements()
    {
      var checkMe = 923180;
      var returned = await _uut.FortiSIEMCloudService.GetProductEntitlementsAsync(checkMe);

      await returned.AssertResponseAsync();
      Assert.That(returned.Data[0].SerialNumber != null);
      Assert.That(returned.Data[0].SerialNumber.StartsWith("FSMCLD"));

      foreach (var a in returned.Data)
      {
        foreach (var ent in a.Entitlements)
        {
          Assert.That(ent.Quantity > 0, $"serial number: {a.SerialNumber} does not have quantity for {ent.SupportTypeDescription}");
        }
      }

      Assert.Pass(await returned.PrintResponseAsync());
    }

    [Test]
    public async Task GetProductEntitlementsAsync_WithValidAccountAndSerialNumber_ShouldNotBeNull()
    {
      var checkMe = "FSMCLD0000000152";

      var returned = await _uut.FortiSIEMCloudService.GetProductEntitlementsAsync(checkMe);

      await returned.AssertResponseAsync();
      Assert.That(returned.Data[0].SerialNumber != null);
      Assert.That(returned.Data[0].SerialNumber.StartsWith("FSMCLD"));
      Assert.That(1 == returned.Data.Count);

      Assert.Pass(await returned.PrintResponseAsync());
    }

    [Test]
    public async Task GetProductEntitlementsAsync_WithValidAccountAndSerialNumbers_ShouldNotBeNull()
    {
      var checkMe = new List<string>()
      {
        "FSMCLD0000000151",
        "FSMCLD0000000152",
        "FSMCLD0000000153",
        "FSMCLD0000000154",
        "FSMCLD0000000155",
        "FSMCLD0000000156",
        "FSMCLD0000000157",
        "FSMCLD0000000158",
        "FSMCLD0000000159",
        "FSMCLD0000000160",
        "FSMCLD0000000161",
        "FSMCLD0000000165",
        "FSMCLD0000000166",
        "FSMCLD0000000170"
      };

      var returned = await _uut.FortiSIEMCloudService.GetProductEntitlementsAsync(checkMe);

      await returned.AssertResponseAsync();
      Assert.That(returned.Data[0].SerialNumber != null);
      Assert.That(returned.Data[0].SerialNumber.StartsWith("FSMCLD"));
      Assert.That(14 == returned.Data.Count);

      foreach (var a in returned.Data)
      {
        foreach (var ent in a.Entitlements)
        {
          Assert.That(ent.Quantity > 0, $"serial number: {a.SerialNumber} does not have quantity for {ent.SupportTypeDescription}");
        }
      }

      Assert.Pass(await returned.PrintResponseAsync());
    }

    [Test]
    public async Task GetLicenseKey_WithValidSerialNumbAndUUID_ShouldNotBeNull()
    {
      var checkMe = "FSMCLD0000000156";
      var uuid = "EC236317-4030-32C4-1BD4-96509A1A9F29";

      var returned = await _uut.FortiSIEMCloudService.GetLicenseKeyAsync(checkMe, uuid);
      await returned.AssertResponseAsync();
      var convertedData = Convert.FromBase64String(returned.Data.LicenseKey);

      Assert.That(returned.Data.SerialNumber != null);
      Assert.That(returned.Data.LicenseKey != null);
      Assert.That(convertedData != null);

      Assert.Pass(await returned.PrintResponseAsync());
    }
  }
}

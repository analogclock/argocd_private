using System;
using System.Linq;
using System.Threading.Tasks;
using FortinetOne.Client.Model;
using NUnit.Framework;

namespace FortinetOne.Client.Tests.Services
{
  [TestFixture]
  internal class CommonServiceTests
  {
    private FoClient _uut;

    [SetUp]
    public void SetUp()
    {
      var cert = CertificateUtilsExtensions.LoadTestCertificate();
      _uut = new FoClient(TestConsts.TestServer, new TestHttpHandler(cert));
    }

    [Test]
    public async Task GetCommonDataAsync_ShouldSucceed()
    {
      var returned = await _uut.CommonService.GetCommonDataAsync();

      await returned.AssertResponseAsync();
      var fortisiem = returned.Data.PortalMenuItems.FirstOrDefault(x => x.AppName.ToLowerInvariant() == "fortisiem");
      Assert.That(fortisiem != null);
    }

    [Test]
    public async Task GetCommonDataLastUpdateTimeAsync_ShouldSucceed()
    {
      var returned = await _uut.CommonService.GetCommonDataLastUpdateTimeAsync();

      await returned.AssertResponseAsync();
      Assert.That(new DateTimeOffset().ToString("o") != returned.Data.LastUpdatedTime.ToString("o"));
    }

    [Test]
    public async Task GetPortalListAsnc_WithRequest_ShouldSucceed()
    {
      var returned = await _uut.CommonService.GetPortalListAsync();

      await returned.AssertResponseAsync();
      var fortisiem = returned.Data.FirstOrDefault(x => x.AppName.ToLowerInvariant() == "fortisiem");
      Assert.That(fortisiem != null);
    }

    [Test]
    public async Task GetFortiCloudLogoAsync_WithRequest_ShouldSucceed()
    {
      var checkMe = new FoSearchFilters()
      {
        AccountId = 923180
      };

      var returned = await _uut.CommonService.GetFortiCloudLogoAsync(checkMe);

      await returned.AssertResponseAsync();
      Assert.That(0 != returned.Data.LogoId);
      Assert.That(returned.Data.HasPremiumSubscription != null);
    }

    [Test]
    public async Task GetFortiCloudPremiumSubscriptionAsync_WithRequest_ShouldSucceed()
    {
      var checkMe = new FoSearchFilters()
      {
        AnAccountId = 923180
      };

      var returned = await _uut.CommonService.GetFortiCloudPremiumSubscriptionAsync(checkMe);

      await returned.AssertResponseAsync();

      Assert.That(returned.Data.HasSubscription != null);
    }

    [Test]
    public async Task GetAccountsByEmailAsync_WithRequest_ShouldSucceed()
    {
      var email = "dhart@fortinet.com";

      var returned = await _uut.CommonService.GetAccountsByEmailAsync(email);

      await returned.AssertResponseAsync();
      Assert.That(returned.Data[0].AccountId != null);
      Assert.That(email == returned.Data[0].AccountEmail);
    }

    [Test]
    public async Task GetAccountDetailsAsync_ByAccountId_ShouldSucceed()
    {
      var checkMe = new FoSearchFilters()
      {
        AccountId = 923180
      };

      var returned = await _uut.CommonService.GetAccountDetailsAsync(checkMe);

      await returned.AssertResponseAsync();
      Assert.That(returned.Data.IsSuperAccount != null);
      Assert.That(checkMe.AccountId == returned.Data.AccountId);
    }

    [Test]
    public async Task GetAccountDetailsAsync_ByAccountEmail_ShouldSucceed()
    {
      var checkMe = new FoSearchFilters()
      {
        AccountEmail = "dhart@fortinet.com"
      };

      var returned = await _uut.CommonService.GetAccountDetailsAsync(checkMe);

      await returned.AssertResponseAsync();
      Assert.That(returned.Data.IsSuperAccount != null);
      Assert.That(checkMe.AccountEmail == returned.Data.AccountEmail);
    }

    [Test]
    public async Task GetAccountDetailsAsync_ByUserId_ShouldSucceed()
    {
      var checkMe = new FoSearchFilters()
      {
        UserId = 98765
      };

      var returned = await _uut.CommonService.GetAccountDetailsAsync(checkMe);

      await returned.AssertResponseAsync();
      Assert.That(returned.Data.IsSuperAccount != null);
      var user = returned.Data.Users.FirstOrDefault(x => x.UserId == checkMe.UserId);
      Assert.That(user != null);
      Assert.That(checkMe.UserId == user.UserId);
    }

    [Test]
    public async Task GetAccountDetailsAsync_BySerialNumber_ShouldSucceed()
    {
      var checkMe = new FoSearchFilters()
      {
        SerialNumber = "FUEBA00000000183"
      };

      var returned = await _uut.CommonService.GetAccountDetailsAsync(checkMe);

      await returned.AssertResponseAsync();
    }

    [Test]
    public async Task GetAccountDetailsAsync_ByIAMInfo_ShouldSucceed()
    {
      var checkMe = new FoSearchFilters()
      {
        IAMUserName = "Ben",
        IAMAccountName = "4983"
      };

      var returned = await _uut.CommonService.GetAccountDetailsAsync(checkMe);

      await returned.AssertResponseAsync();
    }
  }
}

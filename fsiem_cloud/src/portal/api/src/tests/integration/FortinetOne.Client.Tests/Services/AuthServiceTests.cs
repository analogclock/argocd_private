using System.Collections.Generic;
using System.Threading.Tasks;
using FortinetOne.Client.Model;
using NUnit.Framework;

namespace FortinetOne.Client.Tests.Services
{
  [TestFixture]
  internal class AuthServiceTests
  {
    private FoClient _uut;

    [SetUp]
    public void SetUp()
    {
      var cert = CertificateUtilsExtensions.LoadTestCertificate();
      _uut = new FoClient(TestConsts.TestServer, new TestHttpHandler(cert));
    }

    [Test]
    public async Task GetAPIUserPermissionsAsync_ShouldConnect()
    {
      // not a real code - using this to ensure connection is working ok
      var checkMe = new FoSearchFilters()
      {
        AccessToken = "UaFX7SAoTTsQUO0vukvZFzHRpIpzoZ"
      };
      var returned = await _uut.AuthService.GetAPIUserPermissionsAsync(checkMe);

      Assert.That(returned != null);
    }

    [Test]
    public async Task GetUserPermissionsAsync_ByUserEmail_ShouldConnect()
    {
      var accountId = 923180;

      var authAttributes = new List<AuthAttribute>
            {
                new AuthAttribute("NameID", "dhart@fortinet.com"),
                new AuthAttribute("Authentication_status", "password only")
            };

      var returned = await _uut.AuthService.GetUserPermissionsAsync(authAttributes);
      await returned.AssertResponseAsync();
      Assert.That(accountId == returned.Data[0].AccountId);
    }

    [Test]
    public async Task GetUserPermissionsAsync_ByIAMUser_ShouldConnect()
    {
      var authAttributes = new List<AuthAttribute>
            {
                new AuthAttribute("NameID", "iamuser_4983-ben@local-1596056183"),
                new AuthAttribute("Authentication_status", "password only"),
                new AuthAttribute("IAM_account_name", "1124291"),
                new AuthAttribute("IAM_account_alias", "1124291"),
                new AuthAttribute("IAM_username", "Ben"),
            };

      var returned = await _uut.AuthService.GetUserPermissionsAsync(authAttributes);

      await returned.AssertResponseAsync();
    }
  }
}

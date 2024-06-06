using System.Threading.Tasks;
using NUnit.Framework;

namespace FortiMonitor.Client.Tests
{
  [TestFixture]
  public class FortiMonitorClientTests
  {
    // Edit this with a FortiMonitor API token with at least read access
    private static readonly string _apiToken = "";
    private static readonly string _apiUrl = "https://api2.panopta.com/v2";
    private readonly FortiMonitorClient cli = new FortiMonitorClient(_apiUrl, _apiToken);

    [Test]
    public async Task GetServerID_test()
    {
      var resp = await cli.GetServerIDAsync("FSMCLD0000000165", MetricRole.SUPER);
      Assert.That(resp != null);
    }

    [Test]
    public async Task GetMetricID_test()
    {
      var resp = await cli.GetMetricIDAsync("23537252", "Events/Second average 3 min");
      Assert.That(resp != null);
    }

    [Test]
    public async Task GetMetricData_test()
    {
      var resp = await cli.GetMetricDataAsync("23537252", "189286764", "FortiSiem: Events/Second average 3 min");
      Assert.That(resp != null);
    }
  }
}

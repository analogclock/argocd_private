using System.Threading.Tasks;
using FortinetOne.Client.Model.Responses;
using NUnit.Framework;

namespace FortinetOne.Client.Tests.Services
{
  public static class TestHelper
  {
    public static async Task AssertResponseAsync<T>(this FoResponseV3<T> response)
    {
      Assert.That(response != null, "null returned object");
      Assert.That(response.Data != null, await response.PrintResponseAsync());
    }
  }
}

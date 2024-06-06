using FinsProvisioning.Models;
using NUnit.Framework;

namespace FinsProvisioning.Tests.Models
{
  [TestFixture]
  public class DeploymentTests
  {
    [Test]
    public void IsEntitlementValid_NullEntitlement_NotValid()
    {
      var uut = new Deployment();
      Assert.That(!uut.IsEntitlementValid());
    }
  }
}

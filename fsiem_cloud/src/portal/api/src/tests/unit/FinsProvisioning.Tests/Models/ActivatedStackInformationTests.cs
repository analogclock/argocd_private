using FinsProvisioning.Models;
using NUnit.Framework;

namespace FinsProvisioning.Tests.Models
{
  [TestFixture]
  public class ActivatedStackInformationTests
  {

    [TestCase(null, false)] // null
    [TestCase("", false)] // empty
    [TestCase("    ", false)] // whitespace
    [TestCase("password", false)] // not complex enough
    [TestCase("123*Ab", false)] // not long enough
    [TestCase("PassW0rdIsLong", false)] // missing special chars
    [TestCase(@"PassW0rdIsLong*"
      + "PassW0rdIsLong"
      + "PassW0rdIsLong"
      + "PassW0rdIsLong"
      + "PassW0rdIsLong"
      + "PassW0rdIsLong", false)] // too long
    [TestCase("PassW0rdIsLong*", true)] // just right
    public void IsPasswordValid_CheckComplexity(string password, bool isValid)
    {
      var activateInfo = new ActivatedStackInformation()
      {
        AdminPassword = password
      };

      Assert.That(activateInfo.IsValidPassword == isValid);
    }
  }
}

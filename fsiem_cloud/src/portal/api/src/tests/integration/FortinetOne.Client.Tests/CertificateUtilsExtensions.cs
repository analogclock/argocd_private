using System.Security.Cryptography.X509Certificates;
using FinsProvisioning.Helpers;

namespace FortinetOne.Client.Tests
{
  public static class CertificateUtilsExtensions
  {
    public static X509Certificate2 LoadTestCertificate()
    {
      return CertificateUtils.LoadCertificateFromBase64String(TestConsts.Certificate, TestConsts.Passphrase);
    }
  }
}

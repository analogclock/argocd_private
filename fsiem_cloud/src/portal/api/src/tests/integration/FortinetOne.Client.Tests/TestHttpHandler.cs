using System.Net.Http;
using System.Security.Cryptography.X509Certificates;

namespace FortinetOne.Client.Tests
{
  public class TestHttpHandler : HttpClientHandler
  {
    public TestHttpHandler(X509Certificate2 certificate)
    {
      ServerCertificateCustomValidationCallback = (message, certificate2, arg3, arg4) => true;
      if (certificate != null)
      {
        // we have a certificate to add 
        ClientCertificates.Add(certificate);
      }
    }
  }
}

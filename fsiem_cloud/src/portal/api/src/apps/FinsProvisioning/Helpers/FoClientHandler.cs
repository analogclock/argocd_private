using System;
using System.Net.Http;
using System.Security.Cryptography.X509Certificates;

namespace FinsProvisioning.Helpers
{
  /// <summary>
  /// Internal representation of our Secret Value held within AWS
  /// This is used to store both the Passphrase
  /// </summary>
  internal class PassphraseValue
  {
    /// <summary>
    /// Passphrase used for the attached certificate
    /// </summary>
    public string Passphrase { get; set; }
  }

  /// <summary>
  /// Internal representation of our Secret Value held within AWS
  /// This is used to store both the Certificate
  /// </summary>
  internal class CertificateValue
  {
    /// <summary>
    /// Base64 Encoded value of the certificate to use with calls to FortinetOne
    /// </summary>
    public string Certificate { get; set; }
  }

  /// <summary>
  /// FortinetOne client handler
  /// Used to setup the server certificate for calling into the FortinetOne API
  /// </summary>
  public class FoClientHandler : HttpClientHandler
  {
    private readonly X509Certificate2 _certificate;

    public FoClientHandler(ICertificateCache certCache)
    {
      if (certCache == null)
        throw new ArgumentNullException(nameof(certCache));

      _certificate = certCache.Get(CertificateConsts.FortinetOneCertificate);
      Initialize();
    }

    /// <summary>
    /// Setup our handler
    /// We usually just need to do no SSL checks
    /// And
    /// Setup client certificates if applicable
    /// </summary>
    internal void Initialize()
    {
      ServerCertificateCustomValidationCallback = (message, certificate2, arg3, arg4) => true;
      if (_certificate != null)
      {
        // we have a certificate to add 
        ClientCertificates.Add(_certificate);
      }
    }
  }
}

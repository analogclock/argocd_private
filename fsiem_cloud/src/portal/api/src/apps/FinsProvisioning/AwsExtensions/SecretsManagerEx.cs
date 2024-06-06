using System.Security.Cryptography.X509Certificates;
using Amazon.SecretsManager;
using Amazon.SecretsManager.Model;
using FinsProvisioning.Helpers;
using Newtonsoft.Json;

namespace FinsProvisioning.AwsExtensions
{
  public static class SecretsManagerEx
  {
    /// <summary>
    /// Load a given secret as a certificate, give the certificate key and its passphrase
    /// </summary>
    /// <param name="secretsManager">secrets manager to use</param>
    /// <param name="certificateKey">the secret key to use</param>
    /// <param name="passphraseKey">the secret passphrase to use</param>
    /// <returns>a certificate</returns>
    public static X509Certificate2 LoadCertificateFromSecretsManager(this IAmazonSecretsManager secretsManager, string certificateKey, string passphraseKey)
    {
      var certificateRequest = new GetSecretValueRequest
      {
        SecretId = certificateKey,
        VersionStage = "AWSCURRENT"
      };

      var passphraseRequest = new GetSecretValueRequest
      {
        SecretId = passphraseKey,
        VersionStage = "AWSCURRENT"
      };

      string certificateSecret = null;
      string passphraseSecret = null;

      var certificateResponse = secretsManager.GetSecretValueAsync(certificateRequest).Result;
      var passphraseResponse = secretsManager.GetSecretValueAsync(passphraseRequest).Result;

      if (certificateResponse.SecretString != null)
      {
        certificateSecret = certificateResponse.SecretString;
      }

      if (passphraseResponse.SecretString != null)
      {
        passphraseSecret = passphraseResponse.SecretString;
      }

      if (string.IsNullOrWhiteSpace(passphraseSecret) || string.IsNullOrWhiteSpace(certificateSecret))
        return null;

      var passphraseValue = JsonConvert.DeserializeObject<PassphraseValue>(passphraseSecret);
      var certificateValue = JsonConvert.DeserializeObject<CertificateValue>(certificateSecret);
      var certificate = CertificateUtils.LoadCertificateFromBase64String(certificateValue.Certificate, passphraseValue.Passphrase);
      return certificate;
    }
  }
}

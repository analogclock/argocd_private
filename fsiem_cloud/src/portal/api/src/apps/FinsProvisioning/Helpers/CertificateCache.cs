using System;
using System.Collections.Generic;
using System.Security.Cryptography.X509Certificates;
using Amazon.SecretsManager;
using FinsProvisioning.AwsExtensions;
using Microsoft.Extensions.Configuration;

namespace FinsProvisioning.Helpers
{
  public class CertificateConsts
  {
    public const string FortinetOneCertificate = "f1_certificate";
    public const string LicenseSigningCertificate = "fins_license_signing_certificate";
  }

  public interface ICertificateCache
  {
    X509Certificate2 Get(string name);
  }

  /// <summary>
  /// FortinetOne client handler
  /// Used to setup the server certificate for calling into the FortinetOne API
  /// </summary>
  public class CertificateCache : ICertificateCache
  {
    private readonly Dictionary<string, X509Certificate2> _cache;
    private readonly IAmazonSecretsManager _secretsManager;

    private readonly string _fortinetOneCertificateKey;
    private readonly string _fortinetOneCertificatePassphrase;

    private readonly string _licensingCertificateKey;
    private readonly string _licensingCertificatePassphrase;

    public CertificateCache(IAmazonSecretsManager secretsManager, IConfiguration config)
    {
      _secretsManager = secretsManager ?? throw new ArgumentNullException(nameof(secretsManager));
      _cache = new Dictionary<string, X509Certificate2>();

      var fortinetOne = config.GetSection("FortinetOne");
      var certificateKey = fortinetOne.GetValue<string>("CertificateKey");
      var passphraseKey = fortinetOne.GetValue<string>("PassphraseKey");

      var licensingCertificateKey = config.GetValue<string>("LicensingCertificateKey");
      var licensingPassphraseKey = config.GetValue<string>("LicensingPassphraseKey");

      _fortinetOneCertificateKey = certificateKey;
      _fortinetOneCertificatePassphrase = passphraseKey;

      _licensingCertificateKey = licensingCertificateKey;
      _licensingCertificatePassphrase = licensingPassphraseKey;

      Initialize();
    }

    /// <summary>
    /// Setup our certificate caching mechanism this means we do not need to load it during
    /// the start up process and we get the added advantage of DI
    /// </summary>
    internal void Initialize()
    {
      var fortinetOneCertificate =
          _secretsManager.LoadCertificateFromSecretsManager(_fortinetOneCertificateKey,
              _fortinetOneCertificatePassphrase);

      if (fortinetOneCertificate != null)
        _cache.Add(CertificateConsts.FortinetOneCertificate, fortinetOneCertificate);

      var licenseSigningCertificate =
          _secretsManager.LoadCertificateFromSecretsManager(_licensingCertificateKey,
              _licensingCertificatePassphrase);

      if (licenseSigningCertificate != null)
        _cache.Add(CertificateConsts.LicenseSigningCertificate, licenseSigningCertificate);

    }

    public X509Certificate2 Get(string name)
    {
      return _cache.TryGetValue(name, out var cert) ? cert : null;
    }
  }
}

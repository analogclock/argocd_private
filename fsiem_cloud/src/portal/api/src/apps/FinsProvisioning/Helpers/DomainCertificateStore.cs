using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Text;
using System.Threading.Tasks;
using Amazon;
using Amazon.CertificateManager;
using Amazon.CertificateManager.Model;
using FinsProvisioning.Models;

namespace FinsProvisioning.Helpers
{
  public interface IDomainCertificateStore
  {
    /// <summary>
    /// Reset endpoint for specific region where deployment is deployed
    /// </summary>
    /// <param name="serialNumber"></param>
    /// <param name="endpoint"></param>
    /// <returns></returns>
    IDomainCertificateStore With(string serialNumber, RegionEndpoint endpoint = null);
    Task<string> GetAsync(string certificateId);
    Task<bool> DeleteAsync(string certificateId);
    Task<string> SaveAsync(AlternateCertificate certificate, string certificateARN = "");
  }

  public class DomainCertificateStore : IDomainCertificateStore
  {
    private RegionEndpoint _endpoint = RegionEndpoint.USEast1;
    private string _serialNumber = null;

    public IDomainCertificateStore With(string serialNumber, RegionEndpoint endpoint = null)
    {
      _endpoint = endpoint ?? RegionEndpoint.USEast1;
      _serialNumber = serialNumber;
      return this;
    }

    public async Task<string> GetAsync(string certificateId)
    {
      using var client = new AmazonCertificateManagerClient(_endpoint);
      var cert = await client.GetCertificateAsync(certificateId);
      return cert.Certificate;
    }

    public async Task<bool> DeleteAsync(string certificateId)
    {
      using var client = new AmazonCertificateManagerClient(_endpoint);
      var cert = await client.DeleteCertificateAsync(certificateId);
      return cert.HttpStatusCode == HttpStatusCode.OK;
    }

    public async Task<string> SaveAsync(AlternateCertificate certificate, string certificateARN = "")
    {
      if (string.IsNullOrWhiteSpace(certificate.Body))
        throw new ArgumentNullException("body", "Public portion to store cannot be null");

      if (string.IsNullOrWhiteSpace(certificate.Private))
        throw new ArgumentNullException("private", "Private portion to store cannot be null");

      // setup import certificate requests
      // both certificate, and private key are required
      // chain and arn are optional
      // arn will be given to reimport when changes are required
      // only tag if we are dealing with a new certificate
      // we treat updates to certs as re-imports, which means we cannot add tags
      var importCert = new ImportCertificateRequest()
      {
        Certificate = new MemoryStream(Encoding.UTF8.GetBytes(certificate.Body)),
        PrivateKey = new MemoryStream(Encoding.UTF8.GetBytes(certificate.Private)),
        CertificateChain = string.IsNullOrWhiteSpace(certificate.Chain) ? null : new MemoryStream(Encoding.UTF8.GetBytes(certificate.Chain)),
        CertificateArn = string.IsNullOrWhiteSpace(certificateARN) ? null : certificateARN,
        Tags = !string.IsNullOrWhiteSpace(certificateARN) ? null : new List<Tag>() {
          new Tag() {
            Key = "SerialNumber",
            Value = _serialNumber
          }
        }
      };

      using var client = new AmazonCertificateManagerClient(_endpoint);
      var response = await client.ImportCertificateAsync(importCert);

      if (response.HttpStatusCode != System.Net.HttpStatusCode.OK ||
          string.IsNullOrWhiteSpace(response.CertificateArn))
      {
        return null;
      }

      return response.CertificateArn;
    }
  }
}

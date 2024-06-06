using System;
using System.IO;
using System.Reflection;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;

namespace FinsProvisioning.Helpers
{
  public class CertificateUtils
  {
    /// <summary>
    /// Load a certificate from a base 64 encoded string
    /// </summary>
    /// <param name="base64EncodedString">The certificate information represented in a base 64 encoded string</param>
    /// <param name="password">the password used to load the certificate</param>
    /// <returns>and X509Certificate2 representing the certificate loaded from encoded string</returns>
    public static X509Certificate2 LoadCertificateFromBase64String(string base64EncodedString,
        string password = null)
    {
      if (string.IsNullOrWhiteSpace(base64EncodedString))
        return null;

      var decoded = Convert.FromBase64String(base64EncodedString);
      return LoadCertificate(decoded, password);
    }

    /// <summary>
    /// Load certificate from a certificate name found within the Assembly
    /// </summary>
    /// <param name="certificateName">Name of the certificate to load</param>
    /// <param name="password">if there is any password associated with the certificate</param>
    /// <returns>a certificate</returns>
    public static X509Certificate2 LoadCertificate(string certificateName, string password = null)
    {
      var assembly = Assembly.GetCallingAssembly();
      var stream = assembly.GetManifestResourceStream(certificateName);
      if (stream == null)
        throw new ArgumentException(certificateName + " cannot be found as a resource in " + assembly.FullName);
      var bytes = ReadFully(stream);
      return LoadCertificate(bytes, password);
    }

    private static byte[] ReadFully(Stream input)
    {
      var buffer = new byte[16 * 1024];
      using (var ms = new MemoryStream())
      {
        int read;
        while ((read = input.Read(buffer, 0, buffer.Length)) > 0)
        {
          ms.Write(buffer, 0, read);
        }

        return ms.ToArray();
      }
    }

    public static X509Certificate2 LoadCertificate(byte[] certificate, string password)
    {
      try
      {
        return string.IsNullOrWhiteSpace(password)
            ? new X509Certificate2(certificate)
            : new X509Certificate2(certificate, password, X509KeyStorageFlags.Exportable);
        // this certificate must exportable to gain access to the private key
      }
      catch (Exception exception
      ) // we need to retrow now in the .net world as this can fire an internal exception
      {
        throw new CryptographicException(exception.Message, exception);
      }
    }
  }
}

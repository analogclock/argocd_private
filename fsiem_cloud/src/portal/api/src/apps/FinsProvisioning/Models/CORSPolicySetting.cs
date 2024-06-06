using System.Collections.Generic;

namespace FinsProvisioning.Models
{
  public class CORSPolicySetting
  {
    /// <summary>
    /// Origins to allow for CORS settings, such as https://fo.com
    /// </summary>
    public List<string> Origins { get; set; } = new List<string>();

    /// <summary>
    /// Headers to allow for CORS settings, such as X-API, or Content-Type
    /// </summary>
    public List<string> Headers { get; set; } = new List<string>();

    /// <summary>
    /// Methods to allow for CORS settings, such as GET, HEAD, PUT, POST
    /// </summary>
    public List<string> Methods { get; set; } = new List<string>();
  }
}

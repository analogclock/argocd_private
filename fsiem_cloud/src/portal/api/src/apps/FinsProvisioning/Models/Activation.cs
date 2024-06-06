using System;

namespace FinsProvisioning.Models
{
  /// <summary>
  /// An activated stack
  /// </summary>
  public class Activation
  {
    /// <summary>
    /// The id of the activated stack
    /// </summary>
    public string Id { get; set; }

    public Activation(string id)
    {
      if (string.IsNullOrWhiteSpace(id))
        throw new ArgumentNullException(nameof(id));

      Id = id;
    }
  }
}

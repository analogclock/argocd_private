using System;
using Amazon.DynamoDBv2.DocumentModel;
using FinsProvisioning.Extensions;

namespace FinsProvisioning.Models
{
  public class Approval
  {
    public string SerialNumber { get; set; }
    public DateTimeOffset AddedOn { get; set; }
    public bool IsApproved { get; set; } = false;

    /// <summary>
    /// Blank constructor for JSON
    /// </summary>
    public Approval() { }

    public Approval(string serialNumber)
    {
      SerialNumber = serialNumber;
      AddedOn = DateTimeOffset.UtcNow;
      IsApproved = false;
    }

    public Document ToDocument()
    {
      return Document.FromJson(ToJsonString());
    }

    public string ToJsonString()
    {
      return this.SerializeCamel();
    }
  }
}

using FinsProvisioning.Extensions;

namespace FinsProvisioning.Models
{
  public class StackAction
  {
    public const string Apply = "apply";
    public const string Destroy = "destroy";
  }
  /// <summary>
  /// A very simple class to use as an event to deploy a stack
  /// </summary>
  public class Deploy
  {
    public string Name { get; set; }
    public string Action { get; set; }
    public string Region { get; set; }
    public string DeploymentType { get; set; }
    public string DeploymentEmail { get; set; }
    public string DeploymentIPV4Cidr { get; set; }
    public string DeploymentIPV6Cidr { get; set; }

    public string AlternateCertificateARN { get; set; }
    public bool UpdatingDeployment { get; set; } = false;

    public string StorageType { get; set; } = "";

    public ProductSKU DeploymentSKU { get; set; }

    public bool IsPOC { get; set; } = false;

    public bool IsBackupEnabled { get; set; } = true;

    public string PrimaryAZ { get; set; } = null;

    public string ExternalStorageDest { get; set; } = null;

    public Deploy(string action = StackAction.Apply)
    {
      Action = action;
    }

    public string ToJsonString()
    {
      return this.SerializeCamel();
    }
  }
}

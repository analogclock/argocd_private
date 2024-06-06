using System;
using Amazon;
using Amazon.DynamoDBv2.DocumentModel;
using FinsProvisioning.Extensions;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace FinsProvisioning.Models
{
  /// <summary>
  /// Status of the deployment
  /// </summary>
  [JsonConverter(typeof(StringEnumConverter))]
  public enum ActivateStatus
  {
    /// <summary>
    /// Initial Activate has been called
    /// </summary>
    Initializing, // after initial API contact

    /// <summary>
    /// Before the terraform apply has been run
    /// </summary>
    CreateInProgress, // before the terraform apply

    /// <summary>
    ///  After we have performed the initial terraform apply
    /// </summary>
    LicenseInProgress, // after the terraform apply (i.e waiting for a license)

    /// <summary>
    /// Preparing to run the setup container
    /// </summary>
    SetupInitializing,

    /// <summary>
    /// Currently running the setup container
    /// </summary>
    SetupInProgress,

    /// <summary>
    /// Currently running an update to existing deployment
    /// </summary>
    UpdateInProgress,

    /// <summary>
    /// Successfully run update on existing deployment
    /// </summary>
    UpdateCompleted,

    /// <summary>
    /// Failed to update existing deployment
    /// </summary>
    UpdateFailed,

    /// <summary>
    /// Failed to create new deployment
    /// </summary>
    CreateFailed,

    /// <summary>
    /// All deployment tasks completed
    /// </summary>
    Complete,

    /// <summary>
    /// Currently executing Delete stack
    /// </summary>
    DeleteInProgress,

    /// <summary>
    /// Delete has failed.
    /// </summary>
    DeleteFailed
  }

  /// <summary>
  /// Activate object to store deployment information
  /// </summary>
  public class Activate
  {
    /// <summary>
    /// Unique identifier for a deployment
    /// </summary>
    public string SerialNumber { get; set; } = null;

    /// <summary>
    /// Region where this activation should take place
    /// This should relate to the "SystemName" defined
    /// by Amazon
    /// </summary>
    public string Region { get; set; } = null;

    /// <summary>
    /// Gets a display region based on the AWS endpoint name. E.g.: if region is
    /// "us-east-1", this would return "US East (N. Virginia)".
    /// </summary>
    public string DisplayRegion
    {
      get
      {
        if (string.IsNullOrEmpty(Region))
          return string.Empty;
        return RegionEndpoint.GetBySystemName(Region).DisplayName;
      }
    }

    // do not write this information when using JSON
    [JsonIgnore]
    public RegionEndpoint Endpoint
    {
      get
      {
        if (!string.IsNullOrWhiteSpace(Region))
          return RegionEndpoint.GetBySystemName(Region);

        // default to USEEast1
        return RegionEndpoint.USEast1;
      }
    }
    /// <summary>
    /// What stage of the deployment are we at
    /// </summary>
    public ActivateStatus? Status { get; set; } = null;

    /// <summary>
    /// When was this deployment created
    /// </summary>
    public DateTimeOffset? Created { get; set; } = null;

    /// <summary>
    /// Last date time when we inserted the license into the super node
    /// </summary>
    public DateTimeOffset? LicenseInsertedOn { get; set; } = null;

    /// <summary>
    /// Unique identifier for the deployment retrieved via super
    /// </summary>
    public string Uuid { get; set; } = null;

    /// <summary>
    /// Where is the end deployment located
    /// </summary>
    public string Url { get; set; } = null;

    /// <summary>
    /// Public URL for the worker(s)
    /// </summary>
    public string WorkersUrl { get; set; } = null;

    public string DeploymentType { get; set; } = null;

    public string StorageType { get; set; } = null;

    public string DeploymentEmail { get; set; } = null;

    public string AdditionalContacts { get; set; } = null;

    /// <summary>
    /// User provided alternative domain, this must have a stored certificate
    /// to be successful
    /// </summary>
    public string AlternateDomain { get; set; } = null;

    /// <summary>
    /// Stored alternative domain certificate ARN
    /// this determines if there is a successful certificate stored
    /// in ACM
    /// </summary>
    public string AlternateCertificateARN { get; set; } = null;

    // Don't serialize this field, e.g. we don't want to store password in a db
    // Password is received from the user and is stored directly into the
    // secrets manager.
    [JsonIgnore]
    public string AdminPassword { get; set; } = null;

    public string IPV4Cidr { get; set; } = null;
    public string IPV6Cidr { get; set; } = null;

    public ProductSKU DeploymentSKU { get; set; } = null;

    public long OnlineSizeUsage { get; set; } = 0;
    public long ArchiveSizeUsage { get; set; } = 0;
    public string Version { get; set; } = null;

    public bool IsPOC { get; set; } = false;

    public bool IsBackupEnabled { get; set; } = true;

    public string PrimaryAZ { get; set; } = null;

    public string ExternalStorageDest { get; set; } = "";

    public string ExternalStorage { get; set; } = null;

    [JsonIgnore]
    public Version VersionObj
    {
      get
      {
        if (!string.IsNullOrWhiteSpace(Version))
        {
          return new Version(Version);
        }

        return null;
      }
    }

    public Activate()
    { }

    /// <summary>
    /// Create a new activate object for initializing a deployment
    /// </summary>
    public Activate(string serialNumber, string email, ActivatedStackInformation stackInformation, ProductSKU sku, string primaryAZ,
                    bool isPOC = false)
    {
      if (string.IsNullOrWhiteSpace(serialNumber))
        throw new ArgumentException($"'{nameof(serialNumber)}' cannot be null or whitespace.", nameof(serialNumber));
      if (stackInformation == null)
        throw new ArgumentNullException(nameof(stackInformation));

      DeploymentSKU = sku ?? throw new ArgumentNullException(nameof(sku));

      if (sku.Compute.Quantity <= 0)
        throw new ArgumentOutOfRangeException("Compute Quantity", "'Compute Quantity' cannot be less than or equal 0");
      if (sku.OnlineStorage.Quantity <= 0)
        throw new ArgumentOutOfRangeException("Online Storage Quantity", "'Online Storage Quantity' cannot be less than or equal 0");

      SerialNumber = serialNumber;
      Region = stackInformation.RegionEndpoint.SystemName.ToLowerInvariant();
      DeploymentType = stackInformation.DeploymentTypeString.ToLowerInvariant();
      DeploymentEmail = email;
      Status = ActivateStatus.Initializing;
      Created = DateTimeOffset.UtcNow;
      AdminPassword = stackInformation.AdminPassword;

      // default to open to the world should there not be any provided.
      IPV4Cidr = string.IsNullOrWhiteSpace(stackInformation.Ipv4CIDRList) ? "0.0.0.0/0" : stackInformation.Ipv4CIDRList;
      IPV6Cidr = string.IsNullOrWhiteSpace(stackInformation.Ipv6CIDRList) ? "::/0" : stackInformation.Ipv6CIDRList;
      AdditionalContacts = string.IsNullOrWhiteSpace(stackInformation.AdditionalContacts) ? "" : stackInformation.AdditionalContacts;

      StorageType = stackInformation.StorageType;

      DeploymentSKU = sku;
      IsPOC = isPOC;
      PrimaryAZ = primaryAZ;
    }

    /// <summary>
    /// Make activate into a Deploy object
    /// </summary>
    public Deploy ToDeploy(string action = StackAction.Apply,
                           bool updatingDeployment = false)
    {
      return new Deploy(action)
      {
        Name = SerialNumber,
        Region = Region,
        DeploymentEmail = DeploymentEmail,
        DeploymentType = DeploymentType,
        DeploymentIPV4Cidr = IPV4Cidr,
        DeploymentIPV6Cidr = IPV6Cidr,
        UpdatingDeployment = updatingDeployment,
        DeploymentSKU = DeploymentSKU,
        AlternateCertificateARN = AlternateCertificateARN,
        StorageType = StorageType,
        IsPOC = IsPOC,
        PrimaryAZ = PrimaryAZ,
        IsBackupEnabled = IsBackupEnabled,
        ExternalStorageDest = ExternalStorageDest
      };
    }

    /// <summary>
    /// Return JSON serialized string
    /// </summary>
    public string ToJsonString()
    {
      // scrub the password here
      if (!string.IsNullOrWhiteSpace(AdminPassword))
        AdminPassword = null;

      return this.SerializeCamel();
    }

    /// <summary>
    /// Create a DynamoDB Document model
    /// </summary>
    public Document ToDocument()
    {
      return Document.FromJson(ToJsonString());
    }
  }
}

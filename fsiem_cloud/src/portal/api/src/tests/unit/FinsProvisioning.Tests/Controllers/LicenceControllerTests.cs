using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using FinsProvisioning.Controllers;
using FinsProvisioning.Models;
using FinsProvisioning.Services;
using FortinetOne.Client;
using FortinetOne.Client.Model.Responses;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Moq;
using Newtonsoft.Json;
using NUnit.Framework;

namespace FinsProvisioning.Tests.Controllers
{
  [TestFixture]
  public class LicenceControllerTests
  {
    private const int ComputeSupportCode = 224;
    private readonly Mock<ILogger<LicenceController>> _logger = new Mock<ILogger<LicenceController>>();
    private Mock<IActivationService> _activation = new Mock<IActivationService>();
    private Mock<IFoClient> _foClient = new Mock<IFoClient>();

    private LicenceController _uut;

    [SetUp]
    public void SetUp()
    {
      _activation = new Mock<IActivationService>();
      _foClient = new Mock<IFoClient>();
      _uut = new LicenceController(_foClient.Object, _activation.Object, _logger.Object);
    }

    [Test]
    public void Ctor_NullFoClient_Exception()
    {
      var logger = new Mock<ILogger<LicenceController>>();
      var activation = new Mock<IActivationService>();
      Assert.Throws<ArgumentNullException>(() => new LicenceController(null, activation.Object, logger.Object));
    }

    [Test]
    public void ParseLicenceInsertedDate()
    {
      var pythonDate = "2023-05-11 23:02:54.725393";
      var actual = DateTimeOffset.Parse(pythonDate);
      Assert.That(2023 == actual.Year);
    }

    [Test]
    public void IsSameForLicensingPurpose_True()
    {
      var prevEntJson = """
        {
        "Compute": {
          "StartDate": "2022-08-08T00:00:00+00:00",
            "EndDate": "2023-08-08T00:00:00+00:00",
            "ExpiryDays": 88,
            "Quantity": 5
        },
        "OnlineStorage": {
          "StartDate": "2022-08-08T00:00:00+00:00",
            "EndDate": "2024-08-07T00:00:00+00:00",
            "ExpiryDays": 453,
            "Quantity": 1
        },
        "ArchiveStorage": {
          "StartDate": "2022-08-08T00:00:00+00:00",
            "EndDate": "2023-08-08T00:00:00+00:00",
            "ExpiryDays": 88,
            "Quantity": 1
        }
      }
    """;
      var curEntJson = """
       {
        "Compute": {
            "StartDate": "2022-08-08T00:00:00+00:00",
            "EndDate": "2023-08-08T00:00:00+00:00",
            "ExpiryDays": 88,
            "Quantity": 5
        },
        "OnlineStorage": {
            "StartDate": "2022-08-08T00:00:00+00:00",
            "EndDate": "2024-08-07T00:00:00+00:00",
            "ExpiryDays": 453,
            "Quantity": 1
        },
        "ArchiveStorage": {
            "StartDate": "2022-08-08T00:00:00+00:00",
            "EndDate": "2023-08-08T00:00:00+00:00",
            "ExpiryDays": 88,
            "Quantity": 1
        }
      }
    """;
      var prevEnt = JsonConvert.DeserializeObject<ProductSKU>(prevEntJson);
      var curEnt = JsonConvert.DeserializeObject<ProductSKU>(curEntJson);
      Assert.That(prevEnt.IsSameForLicensingPurpose(curEnt));
    }

    [Test]
    public void IsSameForLicensingPurpose_False()
    {
      var prevEntJson = """
        {
        "Compute": {
          "StartDate": "2022-08-08T00:00:00+00:00",
            "EndDate": "2023-08-08T00:00:00+00:00",
            "ExpiryDays": 88,
            "Quantity": 55555555
        },
        "OnlineStorage": {
          "StartDate": "2022-08-08T00:00:00+00:00",
            "EndDate": "2024-08-07T00:00:00+00:00",
            "ExpiryDays": 453,
            "Quantity": 1
        },
        "ArchiveStorage": {
          "StartDate": "2022-08-08T00:00:00+00:00",
            "EndDate": "2023-08-08T00:00:00+00:00",
            "ExpiryDays": 88,
            "Quantity": 1
        }
      }
    """;
      var curEntJson = """
       {
        "Compute": {
            "StartDate": "2022-08-08T00:00:00+00:00",
            "EndDate": "2023-08-08T00:00:00+00:00",
            "ExpiryDays": 88,
            "Quantity": 5
        },
        "OnlineStorage": {
            "StartDate": "2022-08-08T00:00:00+00:00",
            "EndDate": "2024-08-07T00:00:00+00:00",
            "ExpiryDays": 453,
            "Quantity": 1
        },
        "ArchiveStorage": {
            "StartDate": "2022-08-08T00:00:00+00:00",
            "EndDate": "2023-08-08T00:00:00+00:00",
            "ExpiryDays": 88,
            "Quantity": 1
        }
      }
    """;
      var prevEnt = JsonConvert.DeserializeObject<ProductSKU>(prevEntJson);
      var curEnt = JsonConvert.DeserializeObject<ProductSKU>(curEntJson);
      Assert.That(!prevEnt.IsSameForLicensingPurpose(curEnt));
    }

    [Test]
    public async Task Licence_DeploymentNotFound_Forbidden()
    {
      var serial = "test_serial";
      var uuid = "uuid";

      SetupActivation(serial, uuid, null, null, null);

      _foClient
        .Setup(a => a.FortiSIEMCloudService.GetProductEntitlementsAsync(serial))
        .ReturnsAsync(new FoFortiSIEMCloudResponse()
        {
          Data = new List<FoFortiSIEMCloudResponseData>() {
            new FoFortiSIEMCloudResponseData()
            {
              SerialNumber = "totally_different_serial",
              Entitlements = new List<Term>() {
                new Term(){
                  Quantity = 2
                }
              }
            }
          }
        });

      _foClient.Verify(s => s.FortiSIEMCloudService.GetLicenseKeyAsync(It.IsAny<string>(), It.IsAny<string>()), Times.Never());

      var resp = await _uut.Licence(serial, uuid);

      Assert.That(resp.Result, Is.InstanceOf<ObjectResult>());
      var obj = resp.Result as ObjectResult;
      Assert.That(obj.StatusCode == 403);
    }

    [Test]
    public async Task Licence_NullFromFortiCare_Forbidden()
    {
      var serial = "test_serial";
      var uuid = "uuid";

      SetupActivation(serial, uuid, null, null, null);

      _foClient
        .Setup(a => a.FortiSIEMCloudService.GetProductEntitlementsAsync(serial))
        .ReturnsAsync((FoFortiSIEMCloudResponse)null);

      _foClient
        .Verify(s => s.FortiSIEMCloudService.GetLicenseKeyAsync(It.IsAny<string>(), It.IsAny<string>()), Times.Never());

      var resp = await _uut.Licence(serial, uuid);

      Assert.That(resp.Result, Is.InstanceOf<ObjectResult>());
      var obj = resp.Result as ObjectResult;
      Assert.That(obj.StatusCode == 403);
    }

    [Test]
    public async Task Licence_FirstTimeSetup_NullUUID_NullLicenseInsertedOn_Success()
    {
      // expect when first time we provision
      // No UUID returned
      // No License Inserted On field
      // No changes, should return key
      var serial = "test_serial";
      var uuid = "uuid";

      _activation
        .Setup(a => a.GetAsync(serial))
        .ReturnsAsync(new Activate()
        {
          SerialNumber = serial,
          Uuid = null,
          LicenseInsertedOn = null
        });

      SetupLicenseKeyReturn(serial, uuid);

      var resp = await _uut.Licence(serial, uuid);

      Assert.That(resp.Value, Is.InstanceOf<License>());
      var lic = resp.Value as License;
      Assert.That(!lic.HaveDetailsChanged);
      Assert.That(lic.Entitlement == null);
      Assert.That(lic.LicenseKey == "base64Content");
    }

    [Test]
    public async Task Licence_CheckNullsOnLicenseInsertedField_Success()
    {
      // first time setup
      var serial = "test_serial";
      var uuid = "uuid";
      var compiledJson = """
        {
        "LicenseInsertedOn": "",
        "Compute": {
          "StartDate": "2022-08-08T00:00:00+00:00",
            "EndDate": "2023-08-08T00:00:00+00:00",
            "ExpiryDays": 88,
            "Quantity": 55555555
        },
        "OnlineStorage": {
          "StartDate": "2022-08-08T00:00:00+00:00",
            "EndDate": "2024-08-07T00:00:00+00:00",
            "ExpiryDays": 453,
            "Quantity": 1
        },
        "ArchiveStorage": {
          "StartDate": "2022-08-08T00:00:00+00:00",
            "EndDate": "2023-08-08T00:00:00+00:00",
            "ExpiryDays": 88,
            "Quantity": 1
        }
      }
      """;

      var obj = JsonConvert.DeserializeObject<Activate>(compiledJson);
      _activation
        .Setup(a => a.GetAsync(serial))
        .ReturnsAsync(obj);

      SetupLicenseKeyReturn(serial, uuid);

      var resp = await _uut.Licence(serial, uuid);

      Assert.That(resp.Value, Is.InstanceOf<License>());
      var lic = resp.Value as License;
      Assert.That(!lic.HaveDetailsChanged);
      Assert.That(lic.LicenseKey == "base64Content");
    }

    [Test]
    public async Task Licence_HasChanged_HaveDetailsChanged_NewSKU()
    {
      // expect when license has changed between days
      // should return have details changed
      // and present new sku
      var serial = "test_serial";
      var uuid = "uuid";

      SetupActivation(serial, uuid, new IndividualEntitlement()
      {
        Quantity = 1
      });

      SetupEntitlements(serial, new Term()
      {
        SupportType = ComputeSupportCode,
        Quantity = 2
      });

      SetupLicenseKeyReturn(serial, uuid);

      var resp = await _uut.Licence(serial, uuid);

      Assert.That(resp.Value, Is.InstanceOf<License>());
      var lic = resp.Value as License;
      Assert.That(lic.HaveDetailsChanged);
      Assert.That(lic.Entitlement != null);
      Assert.That(lic.Entitlement.Compute.Quantity == 2);
      Assert.That(lic.LicenseKey == "base64Content");
    }

    [Test]
    public async Task Licence_TerraformUpdaterTriggers_NoChanges_DoesNotHaveDetailsChanged_NoSKU()
    {
      // expect that terraform updater is run
      // no changes to underlying license
      // insertLicensedOn field not empty
      // No details changed
      // No entitlements

      var serial = "test_serial";
      var uuid = "uuid";
      var dateToUse = DateTimeOffset.UtcNow;

      SetupActivation(serial, uuid,
        new IndividualEntitlement()
        {
          StartDate = dateToUse,
          EndDate = dateToUse,
          Quantity = 1
        }, insertedOn: DateTimeOffset.UtcNow);

      SetupEntitlements(serial, new Term()
      {
        SupportType = ComputeSupportCode,
        Quantity = 1,
        StartDate = dateToUse,
        EndDate = dateToUse,
      });

      SetupLicenseKeyReturn(serial, uuid);

      var resp = await _uut.Licence(serial, uuid);

      Assert.That(resp.Value, Is.InstanceOf<License>());
      var lic = resp.Value as License;
      Assert.That(!lic.HaveDetailsChanged);
      Assert.That(lic.Entitlement == null);
      Assert.That(lic.LicenseKey == "base64Content");
    }

    [Test]
    public async Task Licence_UserClickedUpdateAndHasChanges_HaveDetailsChanged_NewSKU()
    {
      // expect that license changes update
      // both the InsertedLicenseOn field
      // upload the license to Super
      // and reupload the new SKU

      var serial = "test_serial";
      var uuid = "uuid";
      var dateToUse = DateTimeOffset.UtcNow;

      SetupActivation(serial, uuid, new IndividualEntitlement()
      {
        StartDate = dateToUse,
        EndDate = dateToUse,
        Quantity = 1
      });

      SetupEntitlements(serial, new Term()
      {
        SupportType = ComputeSupportCode,
        Quantity = 2,
        StartDate = dateToUse,
        EndDate = dateToUse,
      });

      SetupLicenseKeyReturn(serial, uuid);
      var resp = await _uut.Licence(serial, uuid);

      Assert.That(resp.Value, Is.InstanceOf<License>());
      var lic = resp.Value as License;
      Assert.That(lic.HaveDetailsChanged);
      Assert.That(lic.Entitlement != null);
      Assert.That(lic.Entitlement.Compute.Quantity == 2);
      Assert.That(lic.LicenseKey == "base64Content");
    }

    [Test]
    public async Task Licence_UserClickedUpdate_NoUnderlyingChangesToSKU()
    {
      // expect that license should be added into Super
      // InsertedLicenseOn should get a value
      // But no need to update SKU on LicenseContainer

      var serial = "test_serial";
      var uuid = "uuid";
      var dateToUse = DateTimeOffset.UtcNow;

      SetupActivation(serial, uuid, new IndividualEntitlement()
      {
        StartDate = dateToUse,
        EndDate = dateToUse,
        Quantity = 1
      });

      SetupEntitlements(serial, new Term()
      {
        SupportType = ComputeSupportCode,
        Quantity = 1,
        StartDate = dateToUse,
        EndDate = dateToUse,
      });

      SetupLicenseKeyReturn(serial, uuid);

      var resp = await _uut.Licence(serial, uuid);

      Assert.That(resp.Value, Is.InstanceOf<License>());
      var lic = resp.Value as License;
      Assert.That(lic.HaveDetailsChanged);
      Assert.That(lic.Entitlement == null);
      Assert.That(lic.LicenseKey == "base64Content");
    }

    private void SetupActivation(string serial, string uuid,
      IndividualEntitlement compute,
      IndividualEntitlement online = null,
      IndividualEntitlement archive = null,
      DateTimeOffset? insertedOn = null)
    {
      _activation
        .Setup(a => a.GetAsync(serial))
        .ReturnsAsync(new Activate()
        {
          SerialNumber = serial,
          LicenseInsertedOn = insertedOn,
          Uuid = uuid,
          DeploymentSKU = new ProductSKU()
          {
            OnlineStorage = online ?? new IndividualEntitlement(),
            ArchiveStorage = archive ?? new IndividualEntitlement(),
            Compute = compute ?? null
          }
        });
    }

    private void SetupEntitlements(string serial, params Term[] terms)
    {
      _foClient
        .Setup(a => a.FortiSIEMCloudService.GetProductEntitlementsAsync(serial))
        .ReturnsAsync(new FoFortiSIEMCloudResponse()
        {
          Data = new List<FoFortiSIEMCloudResponseData>() {
            new FoFortiSIEMCloudResponseData()
            {
              SerialNumber = serial,
              Entitlements = terms.ToList()
            }
          }
        });
    }
    private void SetupLicenseKeyReturn(string serial, string uuid)
    {
      _foClient
          .Setup(a => a.FortiSIEMCloudService.GetLicenseKeyAsync(serial, uuid))
          .ReturnsAsync(new FoFortiSIEMCloudLicenseResponse()
          {
            Data = new FoFortiSIEMCloudLicenseData()
            {
              SerialNumber = serial,
              LicenseKey = "base64Content"
            }
          });
    }
  }
}

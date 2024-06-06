using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Amazon;
using FinsProvisioning.Controllers;
using FinsProvisioning.Helpers;
using FinsProvisioning.Models;
using FinsProvisioning.Tests.Extensions;
using FortinetOne.Client;
using FortinetOne.Client.Model.Responses;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Moq;
using NUnit.Framework;

namespace FinsProvisioning.Tests.Controllers
{
  [TestFixture]
  public class DeploymentControllerTests
  {
    private DeploymentController _uut;
    private Mock<IFoClient> _foClientMock;
    private Mock<IUserManager> _userManagerMock;
    private Mock<IActivator> _activatorMock;
    private Mock<IApprover> _approverMock;
    private Mock<ILogger<DeploymentController>> _loggerMock;

    [SetUp]
    public void SetUp()
    {
      _foClientMock = new Mock<IFoClient>();
      _userManagerMock = new Mock<IUserManager>();
      _activatorMock = new Mock<IActivator>();
      _loggerMock = new Mock<ILogger<DeploymentController>>();
      _approverMock = new Mock<IApprover>();
      _uut = new DeploymentController(_foClientMock.Object,
        _userManagerMock.Object,
        _activatorMock.Object,
        _approverMock.Object,
        _loggerMock.Object);
    }

    [Test]
    public void Ctor_NullFoClient_Exception()
    {
      var foClientMock = new Mock<IFoClient>();
      var userManagerMock = new Mock<IUserManager>();
      var activatorMock = new Mock<IActivator>();
      var approver = new Mock<IApprover>();
      var loggerMock = new Mock<ILogger<DeploymentController>>();
      Assert.Throws<ArgumentNullException>(() =>
      new DeploymentController(
        null,
        userManagerMock.Object,
        activatorMock.Object,
        approver.Object,
        loggerMock.Object));
    }

    [Test]
    public void Ctor_NullUserManager_Exception()
    {
      var foClientMock = new Mock<IFoClient>();
      var userManagerMock = new Mock<IUserManager>();
      var activatorMock = new Mock<IActivator>();
      var approver = new Mock<IApprover>();
      var loggerMock = new Mock<ILogger<DeploymentController>>();

      Assert.Throws<ArgumentNullException>(() =>
      new DeploymentController(
        foClientMock.Object,
        null,
        activatorMock.Object,
        approver.Object,
        loggerMock.Object));
    }

    [Test]
    public void Ctor_NullActivator_Exception()
    {
      var foClientMock = new Mock<IFoClient>();
      var userManagerMock = new Mock<IUserManager>();
      var activatorMock = new Mock<IActivator>();
      var approver = new Mock<IApprover>();
      var loggerMock = new Mock<ILogger<DeploymentController>>();
      Assert.Throws<ArgumentNullException>(() =>
      new DeploymentController(
        foClientMock.Object,
        userManagerMock.Object,
        null,
        approver.Object,
        loggerMock.Object));
    }

    [Test]
    public async Task Activate_NoEntitlement_Forbidden()
    {
      _foClientMock
        .Setup(x => x.FortiSIEMCloudService.GetProductEntitlementsAsync(It.Is<int>(a => a == 12345)))
        .ReturnsAsync(new FoFortiSIEMCloudResponse
        {
          Data = new List<FoFortiSIEMCloudResponseData>()
        }
        );

      var callable = await _uut.Activate(12345, "withSerial", new ActivatedStackInformation() { AdminPassword = "C0mpl#xPassword" });
      Assert.That(callable.Result, Is.InstanceOf<ForbidResult>());
    }

    [Test]
    public async Task Activate_ExistingStack_Forbidden()
    {
      var serial = "fsiem_special_user_fortinet_com-1";

      _foClientMock
        .Setup(x => x.FortiSIEMCloudService.GetProductEntitlementsAsync(It.Is<int>(a => a == 12345)))
        .ReturnsAsync(TestData.CreateAPIResponse(serial));

      _userManagerMock
        .Setup(a => a.GetFortinetIdentityAsync())
        .ReturnsAsync(
          new FortinetIdentity()
          {
            UserId = "special_user"
          }
        );

      _activatorMock
        .Setup(x => x.GetAsync(It.Is<string>(a => a == serial)))
        .ReturnsAsync(
          new Activate()
          {
            SerialNumber = "special_user",
            Url = "a_url"
          }
        );

      var callable = await _uut.Activate(12345, serial, new ActivatedStackInformation() { AdminPassword = "C0mpl#xPassword" });
      Assert.That(callable.Result, Is.InstanceOf<ForbidResult>());
    }

    [Test]
    public async Task Activate_PocNotApproved_Forbidden()
    {
      var serial = "fsiem_special_user_fortinet_com-1";

      _foClientMock
        .Setup(x => x.FortiSIEMCloudService.GetProductEntitlementsAsync(It.Is<int>(a => a == 12345)))
        .ReturnsAsync(
          TestData.CreateAPIResponse(serial)
        );

      _userManagerMock
        .Setup(a => a.GetFortinetIdentityAsync())
        .ReturnsAsync(
          new FortinetIdentity()
          {
            UserId = "special_user"
          }
        );

      _activatorMock
        .Setup(x => x.GetAsync(It.Is<string>(a => a == serial)))
        .ReturnsAsync(
          (Activate)null
        );

      var callable = await _uut.Activate(12345, serial, new ActivatedStackInformation() { AdminPassword = "C0mpl#xPassword" });
      Assert.That(callable.Result, Is.InstanceOf<ForbidResult>());
    }

    [Test]
    public async Task Activate_PocNotApprovedFromTable_Forbidden()
    {
      var serial = "fsiem_special_user_fortinet_com-1";

      _foClientMock
        .Setup(x => x.FortiSIEMCloudService.GetProductEntitlementsAsync(It.Is<int>(a => a == 12345)))
        .ReturnsAsync(
          TestData.CreateAPIResponse(serial)
        );

      _userManagerMock
        .Setup(a => a.GetFortinetIdentityAsync())
        .ReturnsAsync(
          new FortinetIdentity()
          {
            UserId = "special_user"
          }
        );

      _activatorMock
        .Setup(x => x.GetAsync(It.Is<string>(a => a == serial)))
        .ReturnsAsync(
          (Activate)null
        );

      _approverMock
        .Setup(x => x.IsApprovedAsync(It.Is<string>(a => a == serial)))
        .ReturnsAsync(new Approval(serial) { IsApproved = false });

      var callable = await _uut.Activate(12345, serial, new ActivatedStackInformation() { AdminPassword = "C0mpl#xPassword" });

      _approverMock.Verify(x => x.AddAwaitingApprovalAsync(It.Is<string>(a => a == serial)), Times.Never());

      Assert.That(callable.Result, Is.InstanceOf<ForbidResult>());
    }

    [Test]
    public async Task Activate_POCApprovalMissing_Forbidden()
    {
      var serial = "fsiem_special_user_fortinet_com-1";

      _foClientMock
        .Setup(x => x.FortiSIEMCloudService.GetProductEntitlementsAsync(It.Is<int>(a => a == 12345)))
        .ReturnsAsync(
          TestData.CreateAPIResponse(serial)
        );

      _userManagerMock
        .Setup(a => a.GetFortinetIdentityAsync())
        .ReturnsAsync(
          new FortinetIdentity()
          {
            UserId = "special_user"
          }
        );

      _activatorMock
        .Setup(x => x.GetAsync(It.Is<string>(a => a == serial)))
        .ReturnsAsync(
          (Activate)null
        );

      _approverMock
        .Setup(x => x.IsApprovedAsync(It.Is<string>(a => a == serial)))
        .ReturnsAsync((Approval)null);

      var callable = await _uut.Activate(12345, serial, new ActivatedStackInformation() { AdminPassword = "C0mpl#xPassword" });

      _approverMock.Verify(x => x.AddAwaitingApprovalAsync(It.Is<string>(a => a == serial)), Times.Once());

      Assert.That(callable.Result, Is.InstanceOf<ForbidResult>());
    }

    [Test]
    public async Task Activate_POCApproved_Success()
    {
      var serial = "fsiem_special_user_fortinet_com-1";

      _foClientMock
        .Setup(x => x.FortiSIEMCloudService.GetProductEntitlementsAsync(It.Is<int>(a => a == 12345)))
        .ReturnsAsync(
          TestData.CreateAPIResponse(serial)
        );

      _userManagerMock
        .Setup(a => a.GetFortinetIdentityAsync())
        .ReturnsAsync(
          new FortinetIdentity()
          {
            UserId = "special_user"
          }
        );

      _activatorMock
        .Setup(x => x.GetAsync(It.Is<string>(a => a == serial)))
        .ReturnsAsync(
          (Activate)null
        );

      _approverMock
        .Setup(x => x.IsApprovedAsync(It.Is<string>(a => a == serial)))
        .ReturnsAsync(new Approval(serial) { IsApproved = true });

      _activatorMock
        .Setup(x => x.AddAsync(It.Is<Activate>(a => a.IsPOC == true)))
        .ReturnsAsync(
          true
        );

      _activatorMock
        .Setup(x => x.RandomAZAsync(It.Is<RegionEndpoint>(a => a == RegionEndpoint.EUWest1)))
        .ReturnsAsync(
          RegionEndpoint.EUWest1.SystemName
        );

      var callable = await _uut.Activate(12345, serial, new ActivatedStackInformation() { AdminPassword = "C0mpl#xPassword", Region = SupportedRegion.EUWest1 });

      _approverMock.Verify(x => x.AddAwaitingApprovalAsync(It.Is<string>(a => a == serial)), Times.Never());

      Assert.That(callable.Value, Is.InstanceOf<Activation>());
      Assert.That(callable.Value.Id == serial);
    }

    [Test]
    public async Task Activate_EntitlementExpired_UnprocessableEntity()
    {
      var serial = "fsiem_special_user_fortinet_com-1";

      _foClientMock
        .Setup(x => x.FortiSIEMCloudService.GetProductEntitlementsAsync(It.Is<int>(a => a == 12345)))
        .ReturnsAsync(
          TestData.CreateAPIResponse(serial, DateTimeOffset.UtcNow.AddDays(-2))
        );

      _userManagerMock
        .Setup(a => a.GetFortinetIdentityAsync())
        .ReturnsAsync(
          new FortinetIdentity()
          {
            UserId = "special_user"
          }
        );

      var callable = await _uut.Activate(12345, serial, new ActivatedStackInformation() { AdminPassword = "C0mpl#xPassword" });

      _activatorMock.Verify(x => x.GetAsync(It.Is<string>(a => a == serial)), Times.Never());
      _approverMock.Verify(x => x.IsApprovedAsync(It.Is<string>(a => a == serial)), Times.Never());
      _approverMock.Verify(x => x.AddAwaitingApprovalAsync(It.Is<string>(a => a == serial)), Times.Never());

      Assert.That(callable.Result, Is.InstanceOf<UnprocessableEntityResult>());
    }
  }
}

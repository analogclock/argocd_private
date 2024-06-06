using System.Threading.Tasks;
using FinsProvisioning.Controllers;
using FinsProvisioning.Helpers;
using FinsProvisioning.Models;
using FinsProvisioning.Services;
using FinsProvisioning.Tests.Extensions;
using FortinetOne.Client;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Moq;
using NUnit.Framework;

namespace FinsProvisioning.Tests.Controllers
{
  [TestFixture]
  public class UpgradeControllerTests
  {
    private UpgradeController _uut;
    private Mock<IFoClient> _foClientMock;
    private Mock<IActivator> _activatorMock;
    private Mock<IUpdateService> _updateServiceMock;
    private Mock<IScheduledUpgradeService> _scheduleMock;
    private Mock<ILogger<UpgradeController>> _loggerMock;

    [SetUp]
    public void SetUp()
    {
      _foClientMock = new Mock<IFoClient>();
      _loggerMock = new Mock<ILogger<UpgradeController>>();
      _updateServiceMock = new Mock<IUpdateService>();
      _scheduleMock = new Mock<IScheduledUpgradeService>();
      _activatorMock = new Mock<IActivator>();

      _uut = new UpgradeController(_foClientMock.Object,
        _activatorMock.Object,
        _updateServiceMock.Object,
        _scheduleMock.Object,
        _loggerMock.Object
        );
    }

    [Test]
    public async Task UpdateSchedule_InvalidModelState_BadRequest()
    {
      _updateServiceMock
        .Setup(x => x.HasPath(It.Is<string>(a => a == "unknown")))
        .ReturnsAsync(false);
      _uut.ModelState.AddModelError("error", "error");
      var response = await _uut.UpdateScheduled(12345, "serialNumber", new UpgradeUpdateDTO() { UpgradePath = "unknown" });

      Assert.That(response.Result, Is.InstanceOf<BadRequestObjectResult>());
    }

    [Test]
    public async Task UpdateSchedule_UnknownPath_BadRequest()
    {
      _updateServiceMock
        .Setup(x => x.HasPath(It.Is<string>(a => a == "unknown")))
        .ReturnsAsync(false);

      var response = await _uut.UpdateScheduled(12345, "serialNumber", new UpgradeUpdateDTO() { UpgradePath = "unknown" });

      Assert.That(response.Result, Is.InstanceOf<BadRequestObjectResult>());
    }

    [Test]
    public async Task UpdateSchedule_KnownPath_Activation()
    {
      _updateServiceMock
        .Setup(x => x.HasPath(It.Is<string>(a => a == "unknown")))
        .ReturnsAsync(true);

      _scheduleMock
        .Setup(x => x.SaveAsync(It.IsAny<UpgradeModel>()))
        .ReturnsAsync(true);

      _foClientMock
        .Setup(x => x.FortiSIEMCloudService.GetProductEntitlementsAsync(It.Is<int>(a => a == 12345)))
        .ReturnsAsync(TestData.CreateAPIResponse("serialNumber"));

      _activatorMock
        .Setup(x => x.GetAsync(It.Is<string>(y => y == "serialNumber")))
        .ReturnsAsync(new Activate());

      var response = await _uut.UpdateScheduled(12345, "serialNumber", new UpgradeUpdateDTO() { UpgradePath = "unknown" });

      Assert.That(response.Value, Is.InstanceOf<Activation>());
      Assert.That("serialNumber" == response.Value.Id);
    }
  }
}

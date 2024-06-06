using System.Threading.Tasks;
using Amazon.EventBridge;
using Amazon.SimpleSystemsManagement;
using FinsProvisioning.Helpers;
using FinsProvisioning.Models;
using FinsProvisioning.Services;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Moq;
using NUnit.Framework;

namespace FinsProvisioningTests.Helpers
{
  [TestFixture]
  public class DeploymentActivatorTests
  {
    private IActivator _uut;
    private readonly Mock<IAmazonEventBridge> _eventBridge = new Mock<IAmazonEventBridge>();
    private readonly Mock<IActivationService> _dynamoDB = new Mock<IActivationService>();
    private readonly Mock<IAmazonSimpleSystemsManagement> _systemsManagement = new Mock<IAmazonSimpleSystemsManagement>();
    private readonly Mock<IConfiguration> _config = new Mock<IConfiguration>();
    private readonly Mock<ILogger<DeploymentActivator>> _logger = new Mock<ILogger<DeploymentActivator>>();

    [SetUp]
    public void SetUp()
    {
      _uut = new DeploymentActivator(_eventBridge.Object, _systemsManagement.Object, _dynamoDB.Object,
        _config.Object, _logger.Object);
    }

    [TestCase(true, false)]
    [TestCase(false, true)]
    [TestCase(true, true)]
    public async Task UpdateAsync_CurrentOrUpdateIsNUll_False(bool isActivateNull, bool isUpdateNull)
    {
      var current = isActivateNull ? null : new Activate();
      var update = isUpdateNull ? null : new ActivatedStackInformation();

      var result = await _uut.UpdateAsync(current, update);
      Assert.That(!result);
    }

    [TestCase(null)]
    [TestCase("")]
    [TestCase("     ")]
    public async Task UpdateAsync_NullOrEmptySerialNumber_False(string serialNumber)
    {
      var current = new Activate()
      {
        SerialNumber = serialNumber
      };
      var update = new ActivatedStackInformation();

      var result = await _uut.UpdateAsync(current, update);
      Assert.That(!result);
    }

    [Test]
    public async Task UpdateAsync_NoChanges_False()
    {
      var current = new Activate()
      {
        SerialNumber = "no_changes"
      };
      var update = new ActivatedStackInformation();

      var result = await _uut.UpdateAsync(current, update);
      Assert.That(!result);
    }

    [Test]
    public async Task UpdateAsync_UpdateItemFails_False()
    {
      var current = new Activate()
      {
        SerialNumber = "single_change"
      };
      var update = new ActivatedStackInformation()
      {
        AdditionalContacts = "new string"
      };

      _dynamoDB
        .Setup(x => x.UpdateAsync(It.IsAny<Activate>(), It.IsAny<ActivatedStackInformation>()))
        .ReturnsAsync(false);

      var result = await _uut.UpdateAsync(current, update);
      Assert.That(!result);
    }
  }
}

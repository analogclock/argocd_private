using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;
using Amazon.EC2.Model;
using FinsProvisioning.FoResponseExtensions;
using FinsProvisioning.Helpers;
using FinsProvisioning.Models;
using FinsProvisioning.Services;
using FortinetOne.Client;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;

namespace FinsProvisioning.Controllers
{
  [Authorize]
  [ApiController]
  [Route("api/[controller]")]
  public class UpgradeController : ControllerBase
  {
    private readonly IFoClient _foClient;
    private readonly IActivator _deploymentActivator;
    private readonly IUpdateService _updateService;
    private readonly IScheduledUpgradeService _scheduleService;
    private readonly ILogger<UpgradeController> _logger;

    public UpgradeController(IFoClient foClient,
      IActivator deploymentActivator,
      IUpdateService updateService,
      IScheduledUpgradeService scheduledService,
      ILogger<UpgradeController> logger)
    {
      _foClient = foClient ?? throw new ArgumentNullException(nameof(foClient));
      _deploymentActivator = deploymentActivator ?? throw new ArgumentNullException(nameof(deploymentActivator));
      _scheduleService = scheduledService ?? throw new ArgumentNullException(nameof(scheduledService));
      _updateService = updateService ?? throw new ArgumentNullException(nameof(updateService));
      _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    [HttpGet]
    [Route("{accountId:int}/{serialNumber}")]
    public async Task<ActionResult<List<UpgradeModel>>> CheckForScheduled(
      [Required, Range(0, int.MaxValue)] int accountId,
      [Required] string serialNumber
    )
    {
      _logger.LogInformation($"Checking for any scheduled updates for {serialNumber}");

      // first retrieve the entitlements for this account
      // what is this customer allowed
      _logger.LogInformation($"Retrieving entitlements for account: {accountId}");
      var entitled = await _foClient.FortiSIEMCloudService.GetProductEntitlementsAsync(accountId);
      var deployments = entitled.ToDeployments();

      var deployment = deployments.FirstOrDefault(x => x.SerialNumber.ToLowerInvariant() == serialNumber.ToLowerInvariant());
      if (deployment == null)
      {
        _logger.LogError($"Account: {accountId}, attempted to get available update for {serialNumber}, but is forbidden.");
        return Forbid();
      }

      var serial = deployment.SerialNumber;

      // second - check if any have been deployed
      _logger.LogInformation($"Retrieving serial: {serial}");
      var activated = await _deploymentActivator.GetAsync(serial);

      if (activated == null)
      {
        _logger.LogInformation($"Unable to find deployment for: {serialNumber}");
        return NotFound();
      }

      var hasScheduled = await _scheduleService.GetAsync(serialNumber);
      return hasScheduled.Any() ? hasScheduled : new List<UpgradeModel>();
    }

    [HttpPost]
    [Route("{accountId:int}/{serialNumber}")]
    public async Task<ActionResult<Activation>> UpdateScheduled(
      [Required, Range(0, int.MaxValue)] int accountId,
      [Required] string serialNumber,
      [Required, FromBody] UpgradeUpdateDTO updateDto
    )
    {
      _logger.LogInformation($"Updating scheduled upgrade for: {serialNumber}");

      if (!ModelState.IsValid)
      {
        _logger.LogError("Presented model is invalid");
        return BadRequest(ModelState);
      }

      // validate upgrade path
      if (!await _updateService.HasPath(updateDto.UpgradePath))
      {
        // unknown path presented
        ModelState.AddModelError(nameof(updateDto.UpgradePath), "Unable to resolve upgrade path");
        return BadRequest(ModelState);
      }

      // first retrieve the entitlements for this account
      // what is this customer allowed
      _logger.LogInformation($"Retrieving entitlements for account: {accountId}");
      var entitled = await _foClient.FortiSIEMCloudService.GetProductEntitlementsAsync(accountId);
      var deployments = entitled.ToDeployments();

      var deployment = deployments.FirstOrDefault(x => x.SerialNumber.ToLowerInvariant() == serialNumber.ToLowerInvariant());
      if (deployment == null)
      {
        _logger.LogError($"Account: {accountId}, attempted to get available update for {serialNumber}, but is forbidden.");
        return Forbid();
      }

      var serial = deployment.SerialNumber;

      // second - check if any have been deployed
      _logger.LogInformation($"Retrieving serial: {serial}");
      var activated = await _deploymentActivator.GetAsync(serial);

      if (activated == null)
      {
        _logger.LogInformation($"Unable to find deployment for: {serialNumber}");
        return NotFound();
      }

      var hasScheduled = await _scheduleService.SaveAsync(new UpgradeModel(updateDto, serial, UpgradeStatus.Pending));

      if (!hasScheduled)
      {
        _logger.LogError("Unable to schedule upgrade");
        return StatusCode(500);
      }

      return new Activation(serial);
    }
  }
}

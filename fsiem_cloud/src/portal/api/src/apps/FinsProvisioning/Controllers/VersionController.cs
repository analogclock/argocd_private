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
  public class VersionController : ControllerBase
  {
    private readonly IFoClient _foClient;
    private readonly IActivator _deploymentActivator;
    private readonly IUpdateService _updateService;
    private readonly ILogger<VersionController> _logger;

    public VersionController(IFoClient foClient,
      IActivator deploymentActivator,
      IUpdateService updateService,
      ILogger<VersionController> logger)
    {
      _foClient = foClient ?? throw new ArgumentNullException(nameof(foClient));
      _deploymentActivator = deploymentActivator ?? throw new ArgumentNullException(nameof(deploymentActivator));
      _updateService = updateService ?? throw new ArgumentNullException(nameof(updateService));
      _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    [HttpGet]
    [Route("{accountId:int}/{serialNumber}/update")]
    public async Task<ActionResult<List<UpdateModel>>> CheckForUpdate(
      [Required, Range(0, int.MaxValue)] int accountId,
      [Required] string serialNumber
    )
    {
      _logger.LogInformation($"Checking for update for {serialNumber}");

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
        _logger.LogError($"Unable to find deployment for: {serialNumber}");
        return NotFound();
      }

      var versionObj = activated.VersionObj;

      if (versionObj == null)
      {
        _logger.LogError(
          $"Unable to determine activate stack version for: {serialNumber}");
        return NotFound();
      }

      var shortVersion = $"{versionObj.Major}.{versionObj.Minor}.{versionObj.Build}";
      var hasUpdate = await _updateService.CheckForUpdateAsync(shortVersion);
      if (hasUpdate.Any())
      {
        return hasUpdate;
      }

      return new List<UpdateModel>();
    }
  }
}

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
  public class ExternalStorageController : ControllerBase
  {
    private readonly IFoClient _foClient;
    private readonly IActivator _deploymentActivator;
    private readonly ILogger<ExternalStorageController> _logger;
    private readonly IExternalStorageService _externalStorageService;

    public ExternalStorageController(IFoClient foClient,
      IActivator deploymentActivator,
      ILogger<ExternalStorageController> logger,
      IExternalStorageService externalStorageService)
    {
      _foClient = foClient ?? throw new ArgumentNullException(nameof(foClient));
      _deploymentActivator = deploymentActivator ?? throw new ArgumentNullException(nameof(deploymentActivator));
      _logger = logger ?? throw new ArgumentNullException(nameof(logger));
      _externalStorageService = externalStorageService ?? throw new ArgumentNullException(nameof(externalStorageService));
    }

    [HttpGet]
    [Route("{accountId:int?}/{serialNumber}")]
    public async Task<ActionResult<List<ExternalStorage>>> Storages(
      [Required, Range(0, int.MaxValue)] int accountId,
      [Required] string serialNumber)
    {
      // first retrieve the entitlements for this account
      // what is this customer allowed
      _logger.LogInformation($"Retrieving external storages for account: {accountId}");
      var entitled = await _foClient.FortiSIEMCloudService.GetProductEntitlementsAsync(accountId);
      var deployments = entitled.ToDeployments();

      var deployment = deployments.FirstOrDefault(x => x.SerialNumber.ToLowerInvariant() == serialNumber.ToLowerInvariant());
      if (deployment == null)
      {
        _logger.LogError($"Account: {accountId}, attempted to get external storages for {serialNumber}, but is forbidden.");
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

      return await _externalStorageService.Get(serialNumber);
    }

    [HttpDelete]
    [Route("{accountId:int?}/{serialNumber}")]
    public async Task<ActionResult<Activation>> DeleteStorage(
      [Required, Range(0, int.MaxValue)] int accountId,
      [Required] string serialNumber,
      [Required, FromBody] ExternalStorage storage)
    {
      // first retrieve the entitlements for this account
      // what is this customer allowed
      _logger.LogInformation($"Retrieving external storages for account: {accountId}");
      var entitled = await _foClient.FortiSIEMCloudService.GetProductEntitlementsAsync(accountId);
      var deployments = entitled.ToDeployments();

      var deployment = deployments.FirstOrDefault(x => x.SerialNumber.ToLowerInvariant() == serialNumber.ToLowerInvariant());
      if (deployment == null)
      {
        _logger.LogError($"Account: {accountId}, attempted to get external storages for {serialNumber}, but is forbidden.");
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

      // overwrite just in case
      storage.SerialNumber = serial;
      var isDeleted = await _externalStorageService.DeleteAsync(storage);

      return new Activation(storage.Id);
    }

    [HttpPost]
    [Route("{accountId:int}/{serialNumber}")]
    public async Task<ActionResult<Activation>> UpdateStorage(
      [Required, Range(0, int.MaxValue)] int accountId,
      [Required] string serialNumber,
      [Required, FromBody] ExternalStorage storage
    )
    {
      _logger.LogInformation($"Updating External Storage for: {serialNumber}");

      if (!ModelState.IsValid)
      {
        _logger.LogError("Presented model is invalid");
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

      var storageSaved = await _externalStorageService.SaveAsync(storage);

      if (!storageSaved)
      {
        _logger.LogError("Unable to store external storage");
        return StatusCode(500);
      }

      return new Activation(storage.Id);
    }
  }
}


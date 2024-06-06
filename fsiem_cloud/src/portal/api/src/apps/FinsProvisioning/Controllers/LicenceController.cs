using System;
using System.ComponentModel.DataAnnotations;
using System.Threading.Tasks;
using FinsProvisioning.FoResponseExtensions;
using FinsProvisioning.Helpers;
using FinsProvisioning.Models;
using FinsProvisioning.Services;
using FortinetOne.Client;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;

namespace FinsProvisioning.Controllers
{
  /// <summary>
  /// License controller for retrieving a license based on entitlements
  /// </summary>
  // Authorized to only those that can satisfy the following Policy
  [Authorize(Policy = PolicyConsts.CanGenerateLicence)]
  [ApiController]
  [Route("api/[controller]")]
  public class LicenceController : ControllerBase
  {
    private readonly IFoClient _foClient;
    private readonly ILogger<LicenceController> _logger;
    private readonly IActivationService _activationService;

    public LicenceController(IFoClient foClient,
      IActivationService activationService,
      ILogger<LicenceController> logger)
    {
      _foClient = foClient ?? throw new ArgumentNullException(nameof(foClient));
      _logger = logger ?? throw new ArgumentNullException(nameof(logger));
      _activationService = activationService ?? throw new ArgumentNullException(nameof(activationService));
    }

    /// <summary>
    /// Get a license file which will query fortinetone for entitlements based on
    /// the given account id and serial number
    /// </summary>
    /// <param name="serialNumber">the given serial number to get entitlements for</param>
    /// <param name="uuid">Unique HArdware ID for generating the license</param>
    /// <returns>a FortiSIEM license file to be passed into a FortiSIEM stack</returns>
    /// <response code="400">Account id or serial number not provided, or more than a single entitlement has been returned</response>
    /// <response code="403">License cannot be generated</response>
    [HttpGet]
    public async Task<ActionResult<License>> Licence(
      [Required] string serialNumber,
      [Required] string uuid)
    {
      string msg;

      _logger.LogInformation($"License generation called for {serialNumber} and {uuid}");
      _logger.LogInformation($"Check DynamoDB for LicenseInsertedOn value");
      var prevDeploy = await _activationService.GetAsync(serialNumber);

      // always get the license key
      // if we cannot return Forbidden
      _logger.LogInformation("Retrieving license value");
      var resp = await _foClient.FortiSIEMCloudService.GetLicenseKeyAsync(serialNumber, uuid);
      if (resp == null)
      {
        // FortiCare will return us an empty response, when stacks have expired
        // so return 403 to the user
        msg = $"FortiCare did not return license info. Has stack expired? Serial number: {serialNumber}";
        _logger.LogError(msg);
        return StatusCode(StatusCodes.Status403Forbidden, msg);
      }

      var license = resp.ToLicense();
      // default value for have details changed
      license.HaveDetailsChanged = false;

      // If license has previously been inserted, we set date time to show when.
      // We can check if entitlements have changed between previous insertions
      // and current state. This helps mitigate issue when we keep re-inserting
      // the same license every day.
      // we also check if UUID has been set here too
      // this way we can tell if we are upgrading something
      // we also scrub the LicenseInsertedOn when the SKU has changed
      if (prevDeploy.LicenseInsertedOn.HasValue ||
        (!prevDeploy.LicenseInsertedOn.HasValue && !string.IsNullOrWhiteSpace(prevDeploy.Uuid)))
      {
        // this is our normal operation
        // we've already inserted a license
        // so we check if there are any changes
        _logger.LogInformation("license has been deployed before. Checking for any changes in entitlements");
        _logger.LogInformation("Compare entitlements stored in DynamoDB with FortiCare values");

        var currentEntitlement = await GetCurrentSKU(prevDeploy);

        var state = GetLicenseState(prevDeploy, currentEntitlement);
        if (state == LicenseState.NotFound)
        {
          msg = $"No deployment found for {serialNumber}";
          _logger.LogError(msg);
          return StatusCode(StatusCodes.Status403Forbidden, msg);
        }

        // we have either actively clicked on the update button
        // in which case we force update the license
        // or we haven't and its a normal terraform updater
        if (prevDeploy.LicenseInsertedOn.HasValue)
          license.HaveDetailsChanged = state == LicenseState.Changed;
        else
          license.HaveDetailsChanged = true;

        // something has changed with the license
        // we should re-upload with changes
        if (state == LicenseState.Changed)
          license.Entitlement = currentEntitlement;

        _logger.LogInformation($"Have details changed: {license.HaveDetailsChanged}");
        _logger.LogInformation($"License changed state: {state}");
      }

      _logger.LogInformation("Returning license info");
      return license;
    }

    /// <summary>
    /// Get the current SKU from the previous deployment information
    /// </summary>
    /// <param name="previousDeploy">Which SKU to get, to make it current</param>
    /// <returns>Null - no SKU found or the current entitlement</returns>
    [NonAction]
    private async Task<ProductSKU> GetCurrentSKU(Activate previousDeploy)
    {
      var entitled = await _foClient.FortiSIEMCloudService.GetProductEntitlementsAsync(previousDeploy.SerialNumber);
      var deployments = entitled?.ToDeployments();
      var curDeploy = deployments?.Find(x => string.Equals(x.SerialNumber, previousDeploy.SerialNumber, StringComparison.InvariantCultureIgnoreCase));

      return curDeploy?.Entitlement;
    }

    /// <summary>
    /// Get the current license state based on the previous (stored in DB) and the current (retrieved from FortiCare)
    /// </summary>
    /// <param name="previous">previous deployment to check against</param>
    /// <param name="current">current information to check against</param>
    /// <returns></returns>
    [NonAction]
    private LicenseState GetLicenseState(Activate previous, ProductSKU current)
    {
      if (current == null)
        return LicenseState.NotFound;

      var prevDeployJson = JsonConvert.SerializeObject(previous.DeploymentSKU);
      var curDeployJson = JsonConvert.SerializeObject(current);
      _logger.LogInformation($"Previous entitlement: {prevDeployJson}");
      _logger.LogInformation($"Current entitlement: {curDeployJson}");

      return previous.DeploymentSKU.IsSameForLicensingPurpose(current)
        ? LicenseState.NoChange
        : LicenseState.Changed;
    }
  }
}

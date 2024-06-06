using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;
using Amazon.EC2.Model;
using FinsProvisioning.FoResponseExtensions;
using FinsProvisioning.Helpers;
using FinsProvisioning.Models;
using FortinetOne.Client;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;

namespace FinsProvisioning.Controllers
{
  /// <summary>
  /// Retrieve all information for entitled or deployed stacks
  /// Allow deployment of entitled stacks
  /// </summary>
  [Authorize]
  [ApiController]
  [Route("api/[controller]")]
  public class DeploymentController : ControllerBase
  {
    private readonly IFoClient _foClient;
    private readonly IUserManager _userManager;
    private readonly IActivator _deploymentActivator;
    private readonly IApprover _approver;
    private readonly ILogger<DeploymentController> _logger;

    public DeploymentController(IFoClient foClient,
      IUserManager userManager,
      IActivator deploymentActivator,
      IApprover approver,
      ILogger<DeploymentController> logger)
    {
      _foClient = foClient ?? throw new ArgumentNullException(nameof(foClient));
      _userManager = userManager ?? throw new ArgumentNullException(nameof(userManager));
      _deploymentActivator = deploymentActivator ?? throw new ArgumentNullException(nameof(deploymentActivator));
      _logger = logger ?? throw new ArgumentNullException(nameof(logger));
      _approver = approver ?? throw new ArgumentNullException(nameof(approver));
    }

    /// <summary>
    /// Get all information related to a particular account which will include Entitlements, and currently deployed entitlements
    /// </summary>
    /// <param name="accountId">the given id to check activated stacks against</param>
    /// <returns>all activated stacks associated with an account id</returns>
    /// <response code="400">No Account id provided</response>
    [HttpGet]
    [Route("{accountId:int}")]
    public async Task<ActionResult<List<Deployment>>> AllStacks(
      [Required, Range(0, int.MaxValue)] int accountId)
    {
      // first retrieve the entitlements for this account
      // what is this customer allowed
      var deployments = await GetDeployments(accountId);
      var serials = deployments.Select(x => x.SerialNumber).ToList();

      // second - check if any have been deployed
      _logger.LogInformation($"Retrieving any deployment entitlements: {serials.Count} serials to search");
      var stacks = await _deploymentActivator.GetAsync(serials);
      _logger.LogInformation($"Deployed entitlements received: {stacks.Count} found");
      _logger.LogInformation("Applying deployed information to entitlements");
      foreach (var (stack, index, dep) in from stack in stacks
                                          let index = deployments.FindIndex(x => x.SerialNumber.ToLowerInvariant() == stack.SerialNumber.ToLowerInvariant())
                                          where index >= 0
                                          let dep = deployments[index]
                                          select (stack, index, dep))
      {
        _logger.LogInformation($"Applying deployed information to {dep.SerialNumber}");
        dep.Information = stack;
        deployments[index] = dep;
      }

      _logger.LogInformation("Information applied");

      return deployments;
    }

    [HttpGet]
    [Route("{accountId:int}/{serialNumber}")]
    public async Task<ActionResult<Deployment>> Stack(
      [Required, Range(0, int.MaxValue)] int accountId,
      [Required] string serialNumber)
    {
      // first retrieve the entitlements for this account
      // what is this customer allowed
      var deployments = await GetDeployments(accountId);

      var deployment = deployments.FirstOrDefault(x => x.SerialNumber.ToLowerInvariant() == serialNumber.ToLowerInvariant());
      if (deployment == null)
      {
        _logger.LogError($"Account: {accountId}, attempted to get {serialNumber}. But it is forbidden");
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

      _logger.LogInformation($"Found an activated deployment for {activated.SerialNumber}");

      var item = deployments.FirstOrDefault(x => x.SerialNumber.ToLowerInvariant() == activated.SerialNumber.ToLowerInvariant());
      if (item != null)
      {
        item.Information = activated;
      }

      return item;
    }

    /// <summary>
    /// Activate an entitlement, providing account, and serial number
    /// </summary>
    /// <param name="accountId">account id that this serial number is associated with</param>
    /// <param name="serialNumber">the given serial number to activate</param>
    /// <param name="activatedInformation">additional informationt o deploy with the stack</param>
    /// <returns>An ID associated with the activatation to track progress</returns>
    [HttpPut]
    [Route("{accountId:int}/{serialNumber}")]
    public async Task<ActionResult<Activation>> Activate(
      [Required, Range(0, int.MaxValue), FromRoute] int accountId,
      [Required, FromRoute] string serialNumber,
      [Required, FromBody] ActivatedStackInformation activatedInformation)
    {
      if (!activatedInformation.IsValidPassword)
      {
        ModelState.AddModelError("Password", "Admin password does not conform to requirements");
        _logger.LogError("Admin password does not conform to requirements");
        return BadRequest(ModelState);
      }

      var deployments = await GetDeployments(accountId);
      var deployment = deployments.FirstOrDefault(x => x.SerialNumber.ToLowerInvariant() == serialNumber.ToLowerInvariant());
      if (deployment == null)
      {
        _logger.LogError($"Account: {accountId}, attempted to activate {serialNumber}.");
        return Forbid();
      }

      if (!deployment.Entitlement.IsValid())
      {
        _logger.LogError($"Account: {accountId}, attempted to activate {serialNumber} with invalid entitlement");
        // return semantically incorrect request
        return UnprocessableEntity();
      }

      var activateCheck = await _deploymentActivator.GetAsync(serialNumber);
      if (activateCheck != null)
      {
        _logger.LogError($"Attempted to activate an existing stack: {serialNumber}");
        return Forbid();
      }

      // default deployments to not be POCs
      var isPOC = false;
      // POCs will have less than 90 days on their entitlement
      // they must be prior approved by PM, and PMM in order to
      // be kicked off.
      if (deployment.TotalContractDays <= 90)
      {
        var approval = await _approver.IsApprovedAsync(serialNumber);

        if (approval == null || !approval.IsApproved)
        {
          // add to allow us to notify PM, PMM that they need to
          // approve a POC
          if (approval == null)
          {
            // add a new item for approval
            var awaitApproval = await _approver.AddAwaitingApprovalAsync(serialNumber);

            if (awaitApproval)
            {
              _logger.LogInformation($"Added {serialNumber} to approval table, check for approval");
            }
          }

          _logger.LogError($"Attempted to activate {serialNumber} but it hasn't been approved");
          return Forbid();
        }

        // we have an approved POC tell the system that this
        // is the case
        isPOC = true;
      }

      var user = await _userManager.GetFortinetIdentityAsync();

      var randomAZ = await _deploymentActivator.RandomAZAsync(activatedInformation.RegionEndpoint);

      _logger.LogInformation($"{serialNumber} will be deployed into {randomAZ}");
      // create the activation model to send down the pipeline
      var activate = new Activate(serialNumber, user.UserId, activatedInformation, deployment.Entitlement, randomAZ, isPOC);

      // we use the SystemName here to ensure that we are capturing the correct region
      // as defined by Amazon
      _logger.LogInformation($"Activating deployment: {activate.SerialNumber}, in Region: {activatedInformation.RegionEndpoint.SystemName.ToLowerInvariant()}, as a POC: {isPOC}");
      var hasStarted = await _deploymentActivator.AddAsync(activate);
      if (!hasStarted)
      {
        _logger.LogError($"Unable to deploy: {activate.SerialNumber}");
        return StatusCode(StatusCodes.Status500InternalServerError);
      }

      _logger.LogInformation($"Deployed: {activate.SerialNumber}");
      return new Activation(activate.SerialNumber);
    }

    /// <summary>
    /// Update deployed stack
    /// </summary>
    /// <param name="accountId">account id that this SN is associated with</param>
    /// <param name="serialNumber">the given serial number to update</param>
    /// <param name="info">additional information for the stack</param>
    /// <returns>An ID associated with the update to track progress</returns>
    [HttpPost]
    [Route("update/{accountId:int}/{serialNumber}")]
    public async Task<ActionResult<Activation>> Update(
      [Required, Range(0, int.MaxValue), FromRoute] int accountId,
      [Required, FromRoute] string serialNumber,
      [Required, FromBody] ActivatedStackInformation info)
    {
      var deployments = await GetDeployments(accountId);
      var entitlement = deployments.FirstOrDefault(
        x => x.SerialNumber.ToLowerInvariant() == serialNumber.ToLowerInvariant());
      if (entitlement == null)
      {
        _logger.LogError(
          $"Account: {accountId}, not entitled to update sn: {serialNumber}");
        return Forbid();
      }

      var deployment = await _deploymentActivator.GetAsync(serialNumber);
      if (deployment == null)
      {
        _logger.LogError($"Cannot update a stack that isn't deployed: {serialNumber}");
        return Forbid();
      }

      _logger.LogInformation($"Updating deployment: {deployment.SerialNumber}");
      _logger.LogInformation($"Region: {deployment.Region}");
      _logger.LogInformation($"IPV4Cidr: {deployment.IPV4Cidr} ->  {info.Ipv4CIDRList}");
      _logger.LogInformation($"IPV6Cidr: {deployment.IPV6Cidr} ->  {info.Ipv6CIDRList}");
      _logger.LogInformation($"AdditionalContacts: {deployment.AdditionalContacts} ->  {info.AdditionalContacts}");
      _logger.LogInformation($"ShouldUpdateSKU: {info.ShouldUpdateSKU}");

      // do we have a directive to update the SKU (i.e clicked on ApplyUpdate)
      if (info.ShouldUpdateSKU)
      {
        // if we do override the existing deployment sku with the new one
        info.DeploymentSKU = entitlement.Entitlement;
      }

      var hasStarted = await _deploymentActivator.UpdateAsync(deployment, info);
      if (!hasStarted)
      {
        _logger.LogError($"Unable to update sn: {deployment.SerialNumber}");
        return StatusCode(StatusCodes.Status500InternalServerError);
      }

      _logger.LogInformation($"Update scheduled for sn: {deployment.SerialNumber}");
      return new Activation(deployment.SerialNumber);
    }

    [HttpDelete]
    [Route("{accountId:int}/{serialNumber}")]
    public async Task<ActionResult<Activation>> Delete(
      [Required, Range(0, int.MaxValue), FromRoute] int accountId,
      [Required, FromRoute] string serialNumber)
    {
      var deployments = await GetDeployments(accountId);
      var hasEntitlement = deployments.Any(x => x.SerialNumber.ToLowerInvariant() == serialNumber.ToLowerInvariant());
      if (!hasEntitlement)
      {
        _logger.LogError($"Attempted to delete {serialNumber} but account {accountId} is not the owner. Delete has been refused.");
        return Forbid();
      }

      var deployment = await _deploymentActivator.GetAsync(serialNumber);
      if (deployment == null)
      {
        _logger.LogError($"Attempted to delete a non-existing stack: {serialNumber}");
        return Forbid();
      }

      _logger.LogInformation($"Destroying deployment: {serialNumber}");
      var hasDeleted = await _deploymentActivator.DeleteAsync(deployment);
      if (!hasDeleted)
      {
        _logger.LogError($"Unable to delete: {serialNumber}");
        return StatusCode(StatusCodes.Status500InternalServerError);
      }

      _logger.LogInformation($"Deleted: {serialNumber}");
      return new Activation(serialNumber);
    }

    /// <summary>
    /// Get any deployments associated with an account
    /// </summary>
    /// <param name="accountId">Given Account Id to search to deployments</param>
    /// <returns>List of all entitlements</returns>
    private async Task<List<Deployment>> GetDeployments(int accountId)
    {
      _logger.LogInformation($"Retrieving entitlements for account: {accountId}");
      var entitled = await _foClient.FortiSIEMCloudService.GetProductEntitlementsAsync(accountId);
      return entitled.ToDeployments();
    }
  }
}

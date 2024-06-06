using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Threading.Tasks;
using Amazon;
using Amazon.EventBridge;
using Amazon.EventBridge.Model;
using Amazon.SimpleSystemsManagement;
using Amazon.SimpleSystemsManagement.Model;
using FinsProvisioning.AwsExtensions;
using FinsProvisioning.Models;
using FinsProvisioning.Services;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace FinsProvisioning.Helpers
{
  /// <summary>
  /// Activator for deployments
  /// </summary>
  public interface IActivator
  {
    /// <summary>
    /// Add a new deployment to the pipeline
    /// </summary>
    /// <param name="activate">deployment to activate</param>
    /// <returns>
    /// TRUE: Deployment successful
    /// FALSE: Deployment has failed
    /// </returns>
    Task<bool> AddAsync(Activate activate);

    /// <summary>
    /// Update deployment, add it to the pipeline
    /// </summary>
    /// <param name="current">deployment to update</param>
    /// <param name="update">new information to be applied</param>
    /// <returns>
    /// TRUE: Deployment successful
    /// FALSE: Deployment has failed
    /// </returns>
    Task<bool> UpdateAsync(Activate current, ActivatedStackInformation update);

    /// <summary>
    /// Get any deployments by key
    /// </summary>
    /// <param name="key">Unique identifier to retrieve a deployment</param>
    /// <returns>Any active deployments</returns>
    Task<Activate> GetAsync(string key);

    /// <summary>
    /// Get all deployments based on a set of keys
    /// </summary>
    /// <param name="keys">Multiple unique identifiers</param>
    /// <returns>All matching deployments</returns>
    Task<List<Activate>> GetAsync(List<string> keys);

    /// <summary>
    /// Delete an already existing deployment by its key
    /// </summary>
    /// <param name="activate">activation model used for deletion</param>
    /// <returns>boolean determining if it was successful or not</returns>
    Task<bool> DeleteAsync(Activate activate);

    Task<string> RandomAZAsync(RegionEndpoint endpoint);
  }

  public class DeploymentActivator : IActivator
  {
    private const string EventBusKey = "EventBus";

    private const string ActivateSource = "fsiem.deploy.pipeline";

    private readonly string _busName;

    private readonly IAmazonEventBridge _eventBridge;
    private readonly IAmazonSimpleSystemsManagement _systemsManagement;
    private readonly IActivationService _activationService;
    private readonly ILogger<DeploymentActivator> _logger;

    public DeploymentActivator(
      IAmazonEventBridge eventBridge, IAmazonSimpleSystemsManagement systemsManagement,
      IActivationService activationService,
      IConfiguration config,
      ILogger<DeploymentActivator> logger)
    {
      if (config == null)
        throw new ArgumentNullException(nameof(config));

      _activationService = activationService ?? throw new ArgumentNullException(nameof(activationService));
      _eventBridge = eventBridge ?? throw new ArgumentNullException(nameof(eventBridge));
      _systemsManagement = systemsManagement ?? throw new ArgumentNullException(nameof(systemsManagement));
      _logger = logger ?? throw new ArgumentNullException(nameof(logger));
      _busName = config[EventBusKey];
    }

    /// <inheritdoc />
    public async Task<bool> AddAsync(Activate activate)
    {
      if (activate == null)
      {
        _logger.LogError("Activate provided is null");
        return false;
      }

      try
      {
        _logger.LogInformation($"Activating deployment: {activate.SerialNumber}");

        _logger.LogInformation("Adding systems manager parameter key");

        // create a secrets key - step 1
        var putParamReq = new PutParameterRequest()
        {
          Name = $"/{activate.SerialNumber}/admin_password", //place this in a hierarchy for the serial number
          Value = activate.AdminPassword,
          Type = ParameterType.SecureString, // tell the systems manager to encrypt this value
          Overwrite = true // we want to overwrite an existing value
        };

        // add the users password to systems manager parameter store.
        // this will encrypt (by default) the plain text password
        // and make it available further down the line.
        var putParam = await _systemsManagement.PutParameterAsync(putParamReq);

        // we have failed to put the item in systems parameters
        if (putParam.HttpStatusCode != HttpStatusCode.OK)
        {
          _logger.LogError($"Unable to add system param to parameter {activate.SerialNumber}");
          _logger.LogError($"Offending JSON: {activate.ToJsonString()}");
          return false;
        }

        if (!await _activationService.CreateAsync(activate))
        {
          _logger.LogError("Unable to save new activation");
          return false;
        }

        var deployJson = activate.ToDeploy().ToJsonString();

        // now send a request to the pipeline to deploy
        var putEvents = await _eventBridge.PutEventsAsync(
          new PutEventsRequest
          {
            Entries =
            {
              new PutEventsRequestEntry
              {
                Source = ActivateSource,
                EventBusName = _busName,
                DetailType = "NewDeployment",
                Time = DateTimeOffset.UtcNow.UtcDateTime,
                Detail = deployJson
              }
            }
          });

        // we have failed to send to the pipeline
        if (putEvents.HttpStatusCode != HttpStatusCode.OK)
        {
          // we should delete the existing deployment
          // TODO: either delete or update that we have failed
          _logger.LogError($"Unable to add item to event bridge {_busName}");
          _logger.LogError($"Offending JSON: {deployJson}");
          return false;
        }

        _logger.LogInformation($"Deployment for {activate.SerialNumber} scheduled");

        // we are successful
        return true;
      }
      catch (Exception e)
      {
        _logger.LogError(e, $"Unable to add deployment: {e.Message}");
        return false;
      }
    }

    /// <inheritdoc />
    public async Task<bool> UpdateAsync(Activate current, ActivatedStackInformation update)
    {
      if (current == null || update == null)
      {
        _logger.LogError("Update failed, as either current or updated information is null");
        return false;
      }

      if (string.IsNullOrWhiteSpace(current.SerialNumber))
      {
        _logger.LogError("Update cannot be applied to null serial number");
        return false;
      }

      try
      {
        _logger.LogInformation($"Updating deployment: {current.SerialNumber}");

        if (!await _activationService.UpdateAsync(current, update))
        {
          _logger.LogError("Failed to update activation");
          return false;
        }

        // Indicate we are updating an already deployed environment
        var deployJson = current.ToDeploy(updatingDeployment: true).ToJsonString();
        _logger.LogInformation($"Sending event to event bridge: {deployJson}");

        // now send a request to the pipeline to deploy
        var putEvents = await _eventBridge.PutEventsAsync(
          new PutEventsRequest
          {
            Entries =
            {
              new PutEventsRequestEntry
              {
                Source = ActivateSource,
                EventBusName = _busName,
                DetailType = "UpdateDeployment",
                Time = DateTimeOffset.UtcNow.UtcDateTime,
                Detail = deployJson
              }
            }
          });

        // we have failed to send to the pipeline
        if (putEvents.HttpStatusCode != HttpStatusCode.OK)
        {
          // we should delete the existing deployment
          // TODO: either delete or update that we have failed
          _logger.LogError($"Unable to add item to event bridge {_busName}");
          _logger.LogError($"Offending JSON: {deployJson}");
          return false;
        }

        _logger.LogInformation($"Deployment for {current.SerialNumber} scheduled");

        // we are successful
        return true;
      }
      catch (Exception e)
      {
        _logger.LogError(e, $"Unable to add deployment: {e.Message}");
        return false;
      }
    }

    /// <inheritdoc />
    public async Task<bool> DeleteAsync(Activate activate)
    {
      if (activate == null)
      {
        _logger.LogError("Delete failed with null model");
        return false;
      }

      if (string.IsNullOrWhiteSpace(activate.SerialNumber))
      {
        _logger.LogError("Delete failed with null serial number");
        return false;
      }

      try
      {
        _logger.LogInformation($"Delete deployment: {activate.SerialNumber}, in region {activate.Region}");

        // update status to DeleteInProgress
        if (!await _activationService.UpdateStatusAsync(activate.SerialNumber, ActivateStatus.DeleteInProgress))
        {
          _logger.LogError("Unable to update status");
          return false;
        }

        if (!await _systemsManagement.DeleteParameterIfExistsAsync($"/{activate.SerialNumber}/admin_password"))
        {
          _logger.LogError($"Unable to delete system parameter for: {activate.SerialNumber}");
          _logger.LogError($"Offending JSON: {activate.ToJsonString()}");
          return false;
        }

        // setup delete job
        var destroy = activate.ToDeploy(StackAction.Destroy).ToJsonString();

        // now send a request to the pipeline to deploy
        var putEvents = await _eventBridge.PutEventsAsync(
          new PutEventsRequest
          {
            Entries =
            {
              new PutEventsRequestEntry
              {
                Source = ActivateSource,
                EventBusName = _busName,
                DetailType = "DestroyDeployment",
                Time = DateTimeOffset.UtcNow.UtcDateTime,
                Detail = destroy
              }
            }
          });

        // we have failed to send to the pipeline
        if (putEvents.HttpStatusCode != HttpStatusCode.OK)
        {
          // we should delete the existing deployment
          // TODO: either delete or update that we have failed
          _logger.LogError($"Unable to add item to event bridge {_busName}");
          _logger.LogError($"Offending JSON: {destroy}");
          return false;
        }

        _logger.LogInformation($"Destroy for {activate.SerialNumber} scheduled, in region {activate.Region}");

        // we are successful
        return true;
      }
      catch (Exception e)
      {
        _logger.LogError(e, $"Unable to add deployment: {e.Message}");
        return false;
      }
    }

    /// <inheritdoc />
    public async Task<Activate> GetAsync(string key)
    {
      if (string.IsNullOrEmpty(key))
      {
        _logger.LogError("Provided key is null");
        return null;
      }

      try
      {
        _logger.LogInformation($"Getting item with key: {key}");
        var activate = await _activationService.GetAsync(key);
        if (activate == null)
        {
          _logger.LogError($"Unable to find item with key: {key}");
          return null;
        }

        return activate;
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, $"Error getting item: {ex.Message}");
        return null;
      }
    }

    /// <inheritdoc />
    public async Task<List<Activate>> GetAsync(List<string> keys)
    {
      if (keys == null || !keys.Any())
      {
        _logger.LogError("No keys provided");
        return new List<Activate>();
      }

      // I am not sure if I like this or not
      // but it is much easier than using BatchGetItems
      var concurrentBag = new ConcurrentBag<Activate>();

      // TODO: we should chunk this call into 10's, or at least smaller
      var tasks = keys.Distinct().Select(async key =>
      {
        var item = await GetAsync(key);
        if (item != null)
          concurrentBag.Add(item);
      });

      // wait for all tasks to complete
      await Task.WhenAll(tasks);
      return concurrentBag.ToList();
    }

    public async Task<bool> UpdateStatus(string key, ActivateStatus status)
    {
      _logger.LogInformation($"Update status deployment: {key}");

      // update status to DeleteInProgress

      if (!await _activationService.UpdateStatusAsync(key, status))
      {
        _logger.LogError($"Unable to update status");
        _logger.LogError($"Offending key: {key}");
        return false;
      }

      return true;
    }

    public async Task<string> RandomAZAsync(RegionEndpoint endpoint)
    {
      return await endpoint.PickRandomAZAsync();
    }
  }
}

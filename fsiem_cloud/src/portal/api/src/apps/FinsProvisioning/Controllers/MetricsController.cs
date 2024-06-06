using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;
using FinsProvisioning.FoResponseExtensions;
using FinsProvisioning.Helpers;
using FinsProvisioning.Models;
using FinsProvisioning.Services;
using FortiMonitor.Client;
using FortinetOne.Client;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;

namespace FinsProvisioning.Controllers
{
  [Authorize]
  [ApiController]
  [Route("api/[controller]")]
  public class MetricsController : ControllerBase
  {
    private readonly IFoClient _foClient;
    private readonly IActivator _deploymentActivator;
    private readonly IFortiMonitorClient _fortimonitorClient;
    private readonly IMetricsStorageService _storageService;
    private readonly ILogger<MetricsController> _logger;

    public MetricsController(IFoClient foClient,
      IActivator deploymentActivator,
      IFortiMonitorClient fortimonitorClient,
      IMetricsStorageService storageService,
      ILogger<MetricsController> logger)
    {
      _foClient = foClient ?? throw new ArgumentNullException(nameof(foClient));
      _fortimonitorClient = fortimonitorClient ?? throw new ArgumentNullException(nameof(fortimonitorClient));
      _deploymentActivator = deploymentActivator ?? throw new ArgumentNullException(nameof(deploymentActivator));
      _storageService = storageService ?? throw new ArgumentNullException(nameof(storageService));
      _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    [HttpGet]
    [Route("{accountId:int?}/{serialNumber}")]
    public async Task<ActionResult<List<KeyValuePair<DateTimeOffset, double>>>> Metric(
      [Required, Range(0, int.MaxValue)] int accountId,
      [Required] string serialNumber,
      [Required, FromQuery] Metric? metric,
      [FromQuery] MetricTime time = MetricTime.Hour,
      [FromQuery] string role = MetricRole.SUPER)
    {
      // first retrieve the entitlements for this account
      // what is this customer allowed
      _logger.LogInformation($"Retrieving entitlements for account: {accountId}");
      var entitled = await _foClient.FortiSIEMCloudService.GetProductEntitlementsAsync(accountId);
      var deployments = entitled.ToDeployments();

      var deployment = deployments.FirstOrDefault(x => x.SerialNumber.ToLowerInvariant() == serialNumber.ToLowerInvariant());
      if (deployment == null)
      {
        _logger.LogError($"Account: {accountId}, attempted to get metrics for {serialNumber}, but is forbidden.");
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

      // TODO move to a map to allow for reduced if/else if
      var metricName = "";
      if (metric.Value == Models.Metric.Events)
      {
        metricName = MetricConsts.EVENTS;
      }
      else if (metric.Value == Models.Metric.Status)
      {
        metricName = MetricConsts.STATUS;
      }

      _logger.LogInformation($"Retrieving metrics for: {serialNumber}");
      var serverIds = await _fortimonitorClient.GetServerIDAsync(serial, role);

      _logger.LogInformation($"Server ID: {serverIds[0]}");
      var metricIds = await _fortimonitorClient.GetMetricIDAsync(serverIds[0], metricName);

      // For now just get the metrics for the first metric returned
      var metricId = metricIds.FirstOrDefault() ?? "";

      _logger.LogInformation($"Metric ID: {metricId}");
      var metricData = await _fortimonitorClient.GetMetricDataAsync(serverIds[0], metricId, metricName, time);

      _logger.LogInformation($"Retrieved metric data for {serialNumber}");
      return metricData;
    }

    [HttpGet]
    [Route("storage/{accountId:int?}/{serialNumber}")]
    public async Task<ActionResult<PartitionSize>> Storage(
      [Required, Range(0, int.MaxValue)] int accountId,
      [Required] string serialNumber)
    {
      _logger.LogInformation($"Get Clickhouse partition storage info request");

      // first retrieve the entitlements for this account
      // what is this customer allowed
      _logger.LogInformation($"Retrieving entitlements for account: {accountId}");
      var entitled = await _foClient.FortiSIEMCloudService.GetProductEntitlementsAsync(accountId);
      var deployments = entitled.ToDeployments();

      var deployment = deployments.FirstOrDefault(x => x.SerialNumber.ToLowerInvariant() == serialNumber.ToLowerInvariant());
      if (deployment == null)
      {
        _logger.LogError($"Account: {accountId}, attempted to get metrics for {serialNumber}, but is forbidden.");
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

      // Pull partition info from DynamoDb
      _logger.LogInformation($"Retrieving metrics for: {serialNumber}");
      var metrics = await _storageService.Get(serialNumber);
      _logger.LogInformation($"Retrieved metric data for {serialNumber}");

      return metrics;
    }
  }
}

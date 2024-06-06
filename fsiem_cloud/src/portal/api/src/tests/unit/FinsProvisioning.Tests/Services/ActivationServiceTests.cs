using System;
using System.Net;
using System.Threading;
using System.Threading.Tasks;
using Amazon;
using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.Model;
using Amazon.EventBridge;
using Amazon.EventBridge.Model;
using FinsProvisioning.Helpers;
using FinsProvisioning.Models;
using FinsProvisioning.Services;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Moq;
using NUnit.Framework;

namespace FinsProvisioningTests.Services
{
  public class ActivationServiceTests
  {
    private IActivationService _uut;
    private readonly Mock<IAmazonEventBridge> _eventBridge = new Mock<IAmazonEventBridge>();
    private readonly Mock<IAmazonDynamoDB> _dynamoDB = new Mock<IAmazonDynamoDB>();
    private readonly Mock<IConfiguration> _config = new Mock<IConfiguration>();
    private readonly Mock<IDomainCertificateStore> _domainStore = new Mock<IDomainCertificateStore>();
    private readonly Mock<ILogger<Activate>> _logger = new Mock<ILogger<Activate>>();

    [SetUp]
    public void SetUp()
    {
      _config.Setup(a => a["DynamoDbTable"]).Returns("aaa");
      _uut = new ActivationService(_dynamoDB.Object, _domainStore.Object,
        _config.Object, _logger.Object);
    }

    [Test]
    public void Constructor_NullTable_Throws()
    {
      var testConfig = new Mock<IConfiguration>();
      testConfig.Setup(a => a["DynamoDbTable"]).Returns((string)null);

      Assert.Throws<ArgumentNullException>(() => new ActivationService(_dynamoDB.Object, _domainStore.Object,
        testConfig.Object, _logger.Object));
    }

    [TestCase("new_string", null, null, null, "ipV4Cidr")]
    [TestCase(null, "new_string", null, null, "ipV6Cidr")]
    [TestCase(null, null, "new_string", null, "additionalContacts")]
    [TestCase(null, null, null, "new_string", "alternateDomain")]
    public async Task UpdateAsync_SimpleStringSet_HasUpdate(
      string ipv4, string ipv6, string addCon, string altDom,
      string key
    )
    {
      var current = new Activate()
      {
        SerialNumber = "single_change"
      };

      var update = CreateUpdateRequest(
        ipv4, ipv6, addCon, altDom);

      CreateSuccessEventRequest();
      UpdateItemRequest req = null;
      CreateSuccessUpdateRequest((update, cancel) => req = update);

      var result = await _uut.UpdateAsync(current, update);
      _dynamoDB.Verify();
      Assert.That(req != null, "request is not expected to be null");
      Assert.That(2 == req.AttributeUpdates.Count);
      Assert.That(req.AttributeUpdates["status"] != null, "status is not expected to be null");
      Assert.That(req.AttributeUpdates[key] != null, $"{key} is not expected to be null");
      Assert.That(req.AttributeUpdates[key].Value.S == "new_string");
      Assert.That(result);
    }

    [Test]
    public async Task UpdateAsync_FailsToAddCertificate_False()
    {
      var current = new Activate()
      {
        SerialNumber = "single_change",
        Region = "us-east-1"
      };

      var cert = new AlternateCertificate()
      {
        Body = "body_string",
        Private = "private_string",
        Chain = "chain_string"
      };

      var update = CreateUpdateRequest(
        certificate: cert);

      CreateSuccessEventRequest();
      UpdateItemRequest req = null;
      CreateSuccessUpdateRequest((update, cancel) => req = update);
      _domainStore
        .Setup(x => x.With(
          It.Is<string>(s => s == current.SerialNumber),
          It.Is<RegionEndpoint>(re => re == RegionEndpoint.USEast1))
        )
        .Returns(_domainStore.Object);

      _domainStore
        .Setup(x => x.SaveAsync(
          It.IsAny<AlternateCertificate>(),
          It.IsAny<string>()
        ))
        .ReturnsAsync("");

      var result = await _uut.UpdateAsync(current, update);
      Assert.That(!result);
    }

    [Test]
    public async Task UpdateAsync_AddsCertificate_True()
    {
      var current = new Activate()
      {
        SerialNumber = "single_change",
        Region = "us-east-1"
      };

      var cert = new AlternateCertificate()
      {
        Body = "body_string",
        Private = "private_string",
        Chain = "chain_string"
      };

      var update = CreateUpdateRequest(
        certificate: cert);

      CreateSuccessEventRequest();
      UpdateItemRequest req = null;
      CreateSuccessUpdateRequest((update, cancel) => req = update);
      _domainStore
        .Setup(x => x.With(
          It.Is<string>(s => s == current.SerialNumber),
          It.Is<RegionEndpoint>(re => re == RegionEndpoint.USEast1))
        )
        .Returns(_domainStore.Object);

      _domainStore
        .Setup(x => x.SaveAsync(
          It.Is<AlternateCertificate>(
              c => ValidateCert(c, cert)),
          It.IsAny<string>()
        ))
        .ReturnsAsync("certificate_arn");

      var result = await _uut.UpdateAsync(current, update);
      Assert.That(req != null, "request is not expected to be null");
      Assert.That(2 == req.AttributeUpdates.Count);
      Assert.That(req.AttributeUpdates["status"] != null, "status is not expected to be null");
      Assert.That(req.AttributeUpdates["alternateCertificateARN"] != null, $"alternateCertificateARN is not expected to be null");
      Assert.That(req.AttributeUpdates["alternateCertificateARN"].Value.S == "certificate_arn");
      Assert.That(result);
    }

    [Test]
    public async Task UpdateAsync_RemoveAlternateDomain_True()
    {
      var current = new Activate()
      {
        SerialNumber = "single_change",
        AlternateCertificateARN = "not_empty",
        AlternateDomain = "not_empty"
      };

      // clear out the alternate domain
      var update = CreateUpdateRequest(
        alternateDomain: "");

      CreateSuccessEventRequest();
      UpdateItemRequest req = null;
      CreateSuccessUpdateRequest((update, cancel) => req = update);

      var result = await _uut.UpdateAsync(current, update);

      Assert.That(req != null, "request is not expected to be null");
      Assert.That(3 == req.AttributeUpdates.Count);
      Assert.That(req.AttributeUpdates["status"] != null, "status is not expected to be null");
      Assert.That(req.AttributeUpdates["alternateDomain"] != null, $"alternateDomain is not expected to be null");
      Assert.That(req.AttributeUpdates["alternateDomain"].Value.S == "");
      Assert.That(req.AttributeUpdates["alternateCertificateARN"] != null, $"alternateCertificateARN is not expected to be null");
      Assert.That(req.AttributeUpdates["alternateCertificateARN"].Value.S == "");
      Assert.That(result);
    }

    private static bool ValidateCert(AlternateCertificate actual, AlternateCertificate expected)
    {
      return actual.Body == expected.Body &&
        actual.Chain == expected.Chain &&
        actual.Private == expected.Private;
    }

    private void CreateSuccessUpdateRequest(Action<UpdateItemRequest, CancellationToken> func)
    {
      _dynamoDB
        .Setup(x => x.UpdateItemAsync(
          It.IsNotNull<UpdateItemRequest>(), It.IsAny<CancellationToken>()
        ))
        .Callback<UpdateItemRequest, CancellationToken>(func)
        .ReturnsAsync(new UpdateItemResponse()
        {
          HttpStatusCode = HttpStatusCode.OK
        });

    }

    private void CreateSuccessEventRequest()
    {
      _eventBridge
        .Setup(x => x.PutEventsAsync(It.IsAny<PutEventsRequest>(), It.IsAny<CancellationToken>()))
        .ReturnsAsync(new PutEventsResponse()
        {
          HttpStatusCode = HttpStatusCode.OK
        });
    }

    private static ActivatedStackInformation CreateUpdateRequest(
      string ipv4 = null,
      string ipv6 = null,
      string additionContacts = null,
      string alternateDomain = null,
      AlternateCertificate certificate = null
    )
    {
      return new ActivatedStackInformation()
      {
        Ipv4CIDRList = ipv4,
        Ipv6CIDRList = ipv6,
        AdditionalContacts = additionContacts,
        AlternateDomain = alternateDomain,
        Certificate = certificate
      };
    }
  }
}

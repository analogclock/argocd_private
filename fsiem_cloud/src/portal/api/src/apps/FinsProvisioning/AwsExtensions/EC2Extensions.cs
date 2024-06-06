using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Amazon;
using Amazon.EC2;
using Amazon.EC2.Model;

namespace FinsProvisioning.AwsExtensions
{
  /// <summary>
  /// KeyPair key data includes the unencrypted key data, the key and the name of the file
  /// this is usually stored in s3
  /// </summary>
  public class KeyData
  {
    /// <summary>
    /// Key name saved to Ec2 KeyPairs
    /// </summary>
    public string Name { get; set; }

    /// <summary>
    /// Name of the object to store in s3
    /// </summary>
    public string ObjectName { get; set; }

    /// <summary>
    /// Unencrypted key data
    /// </summary>
    public string Data { get; set; }

    public KeyData(string name, string objectName)
    {
      if (string.IsNullOrWhiteSpace(name))
        throw new ArgumentNullException(nameof(name));

      if (string.IsNullOrWhiteSpace(objectName))
        throw new ArgumentNullException(nameof(objectName));

      Name = name.ToLowerInvariant();
      ObjectName = objectName.ToLowerInvariant();
    }

    public KeyData(string name, string objectName, string keyData) : this(name, objectName)
    {
      if (string.IsNullOrWhiteSpace(keyData))
        throw new ArgumentNullException(nameof(keyData));

      Data = keyData;
    }
  }

  public static class Ec2Extensions
  {
    // create one random number generator across the lifetime of the class
    private static readonly Random rng = new Random();

    // We need to only include some AZs when we deploy to certain regions
    // this is because Fargate is only supported in some azs for regions
    // this will allow us to deploy correctly.
    private static readonly Dictionary<RegionEndpoint, List<string>> onlyInclude = new Dictionary<RegionEndpoint, List<string>>()
    {
      {
        RegionEndpoint.CACentral1,
        new List<string>() {
          "cac1-az1",
          "cac1-az2"
        }
      }
    };

    public static KeyData GenerateKeyPair(this IAmazonEC2 client, string serialNumber)
    {
      if (string.IsNullOrWhiteSpace(serialNumber))
        throw new ArgumentNullException(nameof(serialNumber), "serial number cannot be null or empty");

      // check if key pair already exists
      var describeRequest = new DescribeKeyPairsRequest()
      {
        KeyNames = new List<string>()
                {
                    serialNumber.ToLowerInvariant()
                }
      };

      // we already have one created so we just need the name of it
      try
      {
        var exists = client.DescribeKeyPairsAsync(describeRequest).Result;
        if (exists.KeyPairs.Any())
          return new KeyData(exists.KeyPairs[0].KeyName, $"{exists.KeyPairs[0].KeyName}.pem");
      }
      catch (Exception e)
      {
        if (!(e.InnerException is AmazonEC2Exception ec2Exception
            && ec2Exception.ErrorCode.Equals("InvalidKeyPair.NotFound")))
        {
          throw;
        }

        // we will get an exception for key not found but that is ok as we will now create it
      }

      var createRequest = new CreateKeyPairRequest(serialNumber.ToLowerInvariant());

      try
      {
        var result = client.CreateKeyPairAsync(createRequest).Result;
        var keyData = result.KeyPair.KeyMaterial;
        return new KeyData(serialNumber, $"{serialNumber}.pem", keyData);
      }
      catch
      {
        // catch any errors
        return null;
      }
    }

    /// <summary>
    /// Return a single AZ from the given client, the clients region determines which AZs can be used
    /// </summary>
    /// <param name="client"></param>
    /// <param name="exclude"></param>
    /// <returns></returns>
    public static async Task<string> RandomAvailabilityZoneAsync(this IAmazonEC2 client,
      List<string> exclude = null)
    {
      exclude ??= new List<string>();

      // describe all availability zones, which aren't local zones, or wavelength zones
      var request = new DescribeAvailabilityZonesRequest()
      {
        Filters = new List<Filter>() {
          new Filter("opt-in-status", new List<string> {"opt-in-not-required"})
        }
      };

      var response = await client.DescribeAvailabilityZonesAsync(request);

      // select only the ZoneNames (us-east-1a, us-east-1b...)
      // select only the ones that are available at the current time
      var query = response.AvailabilityZones
        .Where(y => y.State == AvailabilityZoneState.Available)
        .Select(x => x);

      if (onlyInclude.TryGetValue(client.Config.RegionEndpoint, out var includeOnly))
      {
        // only return the ones we want based on ZoneId
        query = query.Where(y => includeOnly.Contains(y.ZoneId));
      }

      var azs = query.Select(x => x.ZoneName);

      azs = azs.Except(exclude);

      // pick a random AZ
      return azs.ElementAt(rng.Next(azs.Count()));
    }

    public static async Task<bool> HasAvailableInstanceTypes(this IAmazonEC2 client, List<string> azs,
      List<string> types)
    {
      var request = new DescribeInstanceTypeOfferingsRequest()
      {
        LocationType = LocationType.AvailabilityZone,
        MaxResults = 1000,
        Filters = new List<Filter>() {
          new("location", azs),
          new("instance-type", types)
        }
      };

      var response = await client.DescribeInstanceTypeOfferingsAsync(request);
      return response.InstanceTypeOfferings.Any();
    }

    /// <summary>
    /// Pick a random, available, availability zone within the specified region
    /// </summary>
    /// <param name="endpoint">the given region to pick availability zone from</param>
    /// <returns></returns>
    public static async Task<string> PickRandomAZAsync(this RegionEndpoint endpoint)
    {
      using (IAmazonEC2 client = new AmazonEC2Client(endpoint))
      {
        var failedAzs = new HashSet<string>();
        // try max 10 times.
        for (var limit = 0; limit < 10; limit++)
        {
          var az = await client.RandomAvailabilityZoneAsync(failedAzs.ToList());
          var canUse = true;
          foreach (var instanceTypes in new List<List<string>>() {
            new List<string> { "c6i.*", "c6a.*", "c5.*" },
            new List<string> { "m6i.*", "m6a.*", "m5.*" },
            new List<string> { "r6i.*", "r6a.*", "r5.*" }
          })
          {
            // check if we can use any of the instances on offer
            var isTypeAvailable = await client.HasAvailableInstanceTypes(
              new List<string> { az },
              instanceTypes
            );

            // if one fails we cannot use this AZ at all
            if (!isTypeAvailable)
            {
              canUse = false;
              // break out as one has failed our checks
              break;
            }
          }

          // all three offerings are available to us
          if (canUse)
            return az;

          // exclude for the next run
          failedAzs.Add(az);
        }

        // we aren't able to pick a random az to put the deployment in
        // we should error here.
        throw new Exception($@"Unable to pick random AZ in region ({endpoint.SystemName}) to put deployment in.
          Tried, and failed with {string.Join(",", failedAzs)}");
      }
    }
  }
}

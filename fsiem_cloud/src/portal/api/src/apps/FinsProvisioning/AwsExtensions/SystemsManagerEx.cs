using System;
using System.Net;
using System.Threading.Tasks;
using Amazon.SimpleSystemsManagement;
using Amazon.SimpleSystemsManagement.Model;

namespace FinsProvisioning.AwsExtensions
{
  public static class SystemsManagerEx
  {
    public static async Task<bool> DeleteParameterIfExistsAsync(this IAmazonSimpleSystemsManagement systemsManagement, string name)
    {
      try
      {
        var getParam = new GetParameterRequest()
        {
          Name = name
        };

        // 1. does it exist
        var exists = await systemsManagement.GetParameterAsync(getParam);

        if (exists.HttpStatusCode == HttpStatusCode.OK)
        {
          // 2 it exists - we must delete it
          var deleteParamReq = new DeleteParameterRequest()
          {
            Name = name
          };

          var deleteParam = await systemsManagement.DeleteParameterAsync(deleteParamReq);

          // we have failed to delete the item in systems parameters
          if (deleteParam.HttpStatusCode != HttpStatusCode.OK)
          {
            // we have failed to delete
            // stop the process
            return false;
          }
        }
      }
      catch (ParameterNotFoundException)
      {
        // the parameter wasn't found
        // so we are actually successful
        return true;
      }
      catch (Exception)
      {
        // we have an unhandled exception here
        // rethrow to catch it.
        throw;
      }

      // we are successful
      return true;
    }
  }
}

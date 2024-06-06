using System;
using System.Threading.Tasks;
using Amazon.Lambda.APIGatewayEvents;
using Amazon.Lambda.Core;
using Amazon.Lambda.RuntimeSupport;
using Amazon.Lambda.Serialization.SystemTextJson;
using Microsoft.AspNetCore;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Hosting;

namespace FinsProvisioning
{
  /// <summary>
  /// The Main function can be used to run the ASP.NET Core application locally using the Kestrel webserver.
  /// </summary>
  public class LocalEntryPoint
  {
    public static void Main(string[] args)
    {
      // we are either running in Local Mode (i.e local debug)
      // or we are running under Lambda      
      if (string.IsNullOrEmpty(Environment.GetEnvironmentVariable("AWS_LAMBDA_FUNCTION_NAME")))
      {
        CreateWebHostBuilder(args).Build().Run();
      }
      else
      {
        // we are running within the Lambda environment
        // so create our LambdaEntryPoint and pass it to the
        // bootstrapper ready for execution
        var lambdaEntry = new LambdaEntryPoint();
        var functionHandler = (Func<APIGatewayProxyRequest, ILambdaContext, Task<APIGatewayProxyResponse>>)lambdaEntry.FunctionHandlerAsync;
        using var handlerWrapper = HandlerWrapper.GetHandlerWrapper(functionHandler, new DefaultLambdaJsonSerializer());
        using var bootstrap = new LambdaBootstrap(handlerWrapper);
        bootstrap.RunAsync().Wait();
      }
    }

    /// <summary>
    /// Create a standard web host builder, which will use kestrel locally
    /// </summary>
    /// <param name="args">ay arguments passed to the executable</param>
    /// <returns>the webhost builder ready for running</returns>
    public static IWebHostBuilder CreateWebHostBuilder(string[] args) =>
                WebHost.CreateDefaultBuilder(args)
                        .UseStartup<Startup>();
  }
}

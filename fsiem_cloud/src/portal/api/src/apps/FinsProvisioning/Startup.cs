using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Amazon.CertificateManager;
using Amazon.CognitoIdentityProvider;
using Amazon.DynamoDBv2;
using Amazon.EC2;
using Amazon.EventBridge;
using Amazon.S3;
using Amazon.SecretsManager;
using Amazon.SecretsManager.Model;
using Amazon.SimpleSystemsManagement;
using FinsProvisioning.Helpers;
using FinsProvisioning.Helpers.Caches;
using FinsProvisioning.Middleware;
using FinsProvisioning.Models;
using FinsProvisioning.Services;
using FortiMonitor.Client;
using FortinetOne.Client;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.ResponseCompression;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi.Models;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace FinsProvisioning
{
  public class Startup
  {
    public Startup(IConfiguration configuration)
    {
      Configuration = configuration;
    }

    public static IConfiguration Configuration { get; private set; }

    // This method gets called by the runtime. Use this method to add services to the container
    public void ConfigureServices(IServiceCollection services)
    {
      // fortinet one URL information
      var fortinetOne = Configuration.GetSection("FortinetOne");
      var baseUrl = fortinetOne.GetValue<string>("BaseUrl");

      var cognito = Configuration.GetSection("Cognito");
      var openIdConfig = cognito.GetValue<string>("OpenIdConfigLocation");
      var fortinetOneClientId = cognito.GetValue<string>("FortinetOneClientId");
      var cache = Configuration.GetSection("PortalListCache");
      var cacheType = cache.GetValue("CacheType", PortalListCacheType.Memory);
      var dynamoDbTable = Configuration.GetValue("DynamoDbTable", "fsiem_activation_table_dev");
      var eventBusName = Configuration.GetValue("EventBus", "portal-bus-dev");
      var fortiMonitor = Configuration.GetSection("FortiMonitor");
      var tokenKey = fortiMonitor.GetValue<string>("TokenKey");
      var apiUrl = fortiMonitor.GetValue<string>("ApiUrl");
      var environment = Configuration.GetValue("Environment", "playground");
      var corsPolicy = Configuration.GetSection("CorsPolicy");

      services.AddAuthentication(options =>
          {
            options.DefaultAuthenticateScheme = "FortinetOne";
            options.DefaultChallengeScheme = "FortinetOne";
          })
          .AddJwtBearer("FortinetOne", options =>
              {
                options.MetadataAddress = openIdConfig;
                options.SaveToken = true; // allow us to use the token from httpcontext
                options.IncludeErrorDetails = false; // don't let out any error details on headers
                options.TokenValidationParameters = new TokenValidationParameters
                {
                  ValidateAudience = false // cognito does not provide the `aud` as part of the token, and therefore cannot be validated
                };
              }
          )
          .AddJwtBearer("Licence", licenceOptions =>
              {
                // we still use the same meta address to validate the access_token
                // this will allow the licence calls to be done
                // but this access token cannot access the FortinetOne logins
                licenceOptions.MetadataAddress = openIdConfig;
                licenceOptions.SaveToken = false;
                licenceOptions.IncludeErrorDetails = false;
                licenceOptions.TokenValidationParameters = new TokenValidationParameters
                {
                  ValidateAudience =
                              false // you do not need to validate the audience during the access token checks
                                    // this is because access_tokens does not provide it and it is only available in an id_token
                };
              }
          )
          .AddJwtBearer("Status", statusOptions =>
          {
            // we still use the same meta address to validate the access_token
            // this will allow the status calls to be done
            // but this access token cannot access the FortinetOne logins
            statusOptions.MetadataAddress = openIdConfig;
            statusOptions.SaveToken = false;
            statusOptions.IncludeErrorDetails = false;
            statusOptions.TokenValidationParameters = new TokenValidationParameters
            {
              ValidateAudience =
                          false // you do not need to validate the audience during the access token checks
                                // this is because access_tokens does not provide it and it is only available in an id_token
            };
          }
          );

      // add specific authorization policies based on the scope of the user
      services.AddAuthorization(options =>
      {
        // ensure that only the given provided to licence can actually generate a licence
        options.AddPolicy(PolicyConsts.CanGenerateLicence, retrieveLicence =>
        {
          retrieveLicence.AddAuthenticationSchemes("Licence");
          retrieveLicence.RequireAuthenticatedUser();
          retrieveLicence.RequireAssertion(ctx => ctx.User.HasClaim("scope", "licence/licence.get"));
        });
      });

      services.AddResponseCompression(x =>
      {
        x.EnableForHttps = true;
        x.Providers.Add<GzipCompressionProvider>();
        x.Providers.Add<BrotliCompressionProvider>();
      });

      services.AddMvc().AddNewtonsoftJson();

      // add swagger documentation
      services.AddSwaggerGen(gen =>
      {
        gen.SwaggerDoc("v1", new OpenApiInfo()
        {
          Title = "Provisioning API",
          Description =
                "Provisioning API used to activate FortiSIEM stacks, support single signon from FortinetOne and generate a licence file",
          Version = "v1",
        });

        var xmlFile = $"{Assembly.GetExecutingAssembly().GetName().Name}.xml";
        var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
        gen.IncludeXmlComments(xmlPath);
      });

      // add .net core capabilities
      // setup CORS policy to only set valid origins
      services.AddCors(options =>
        options.AddPolicy("CORS_API_POLICY", cors =>
        {
          if (!corsPolicy.Exists())
          {
            // we do not have a cors policy defined
            // return allow all
            cors.AllowAnyOrigin().AllowAnyHeader().AllowAnyMethod();
            return;
          }

          // extract settings from the AppSettings domain
          var corsSettings = corsPolicy.Get<CORSPolicySetting>();

          if (corsSettings.Origins.Any())
            cors.WithOrigins(corsSettings.Origins.ToArray());
          else
            cors.AllowAnyOrigin();

          if (corsSettings.Headers.Any())
            cors.WithHeaders(corsSettings.Headers.ToArray());
          else
            cors.AllowAnyHeader();

          if (corsSettings.Methods.Any())
            cors.WithMethods(corsSettings.Methods.ToArray());
          else
            cors.AllowAnyMethod();
        })
      );
      services.AddMemoryCache();

      services.AddDefaultAWSOptions(Configuration.GetAWSOptions());

      // Add AWS Services
      services.AddAWSService<IAmazonS3>();
      services.AddAWSService<IAmazonSecretsManager>();
      services.AddAWSService<IAmazonSimpleSystemsManagement>();
      services.AddAWSService<IAmazonEventBridge>();
      services.AddAWSService<IAmazonEC2>();
      services.AddAWSService<IAmazonDynamoDB>();
      services.AddAWSService<IAmazonCertificateManager>();
      services.AddAWSService<IAmazonCognitoIdentityProvider>();

      // Add Our Services
      services.AddHttpContextAccessor();
      services.AddTransient<IUserManager, UserManager>();
      services.AddSingleton<ICertificateCache, CertificateCache>();
      services.AddSingleton<IDomainCertificateStore, DomainCertificateStore>();
      services.AddSingleton<IActivator, DeploymentActivator>();
      services.AddSingleton<IApprover, Approver>();
      services.AddSingleton<IUpdateService, UpdateService>();
      services.AddSingleton<IScheduledUpgradeService, ScheduledUpgradeService>();
      services.AddSingleton<IActivationService, ActivationService>();
      services.AddSingleton<IExternalStorageService, ExternalStorageService>();
      services.AddSingleton<IMetricsStorageService, MetricsStorageService>();
      services.AddSingleton<IFortiMonitorClient>(options =>
      {
        var certificateRequest = new GetSecretValueRequest
        {
          SecretId = tokenKey,
          VersionStage = "AWSCURRENT"
        };
        var secrets = options.GetService<IAmazonSecretsManager>();
        var token = secrets.GetSecretValueAsync(certificateRequest).Result;
        var secretValue = JsonConvert.DeserializeObject<JObject>(token.SecretString);

        // set timeout to 5 minutes
        // this resolves an issue where some calls to FortiMonitor can take a considerable
        // time
        return new FortiMonitorClient(apiUrl: apiUrl,
          token: secretValue["api_key"].ToString(),
          environment: environment,
          timeoutSeconds: 600);
      });
      services.AddSingleton<IFoClient>(options =>
          new FoClient(baseUrl, new FoClientHandler(options.GetService<ICertificateCache>())));

      switch (cacheType)
      {
        case PortalListCacheType.File:
          {
            var location = cache.GetValue("Location", "local.common_data");
            // default to roughly 10 minutes
            var daysToKeep = cache.GetValue("DaysToKeep", 0.007);

            services.AddSingleton<IMenuCache>(options => new CommonDataPersistentCache(
                    options.GetService<IFoClient>(),
                    new FileBasedCommonDataCache(location),
                    TimeSpan.FromDays(daysToKeep).TotalSeconds
                ));
            break;
          }
        case PortalListCacheType.S3:
          {
            var bucketName = cache.GetValue("BucketName", "zfdevdeploy");
            var keyName = cache.GetValue("KeyName", "common_data");
            // default to roughly 10 minutes
            var daysToKeep = cache.GetValue("DaysToKeep", 0.007);

            services.AddSingleton<IMenuCache>(options => new CommonDataPersistentCache(
                    options.GetService<IFoClient>(),
                    new S3CommonDataCache(options.GetService<IAmazonS3>(), bucketName, keyName),
                    TimeSpan.FromDays(daysToKeep).TotalSeconds
                ));
            break;
          }
        default:
          services.AddSingleton<IMenuCache>(options => new MenuCache(options.GetService<IFoClient>()));
          break;
      }
    }

    // This method gets called by the runtime. Use this method to configure the HTTP request pipeline
    public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
    {
      app.UseHttpsRedirection();

      if (env.IsDevelopment())
      {
        app.UseDeveloperExceptionPage();
        app.UseStaticFiles();
        app.UseSwagger();
        app.UseSwaggerUI(ctx =>
        {
          ctx.SwaggerEndpoint("/swagger/v1/swagger.json", "Provisioning API");
          ctx.RoutePrefix = string.Empty;
        });
      }
      else
      {
        app.UseHsts();
        // add all our required headers
        app.UseMiddleware<SecurityHeadersMiddleware>();
      }

      app.UseCors("CORS_API_POLICY");
      app.UseResponseCompression();
      app.UseRouting();
      app.UseAuthentication();
      app.UseAuthorization();

      app.UseEndpoints(endpoints =>
      {
        endpoints.MapControllers();
      });
    }
  }
}

// Taken from blog post https://arminzia.com/blog/the-aspnet-core-security-headers-guide/#:~:text=Headers%20for%20improved%20security%20%C2%B7%20X%2DFrame%2DOptions%20%C2%B7,X%2DContent%2DType%2DOptions%20%C2%B7%20Referrer%2DPolicy%20%C2%B7%20X%2DPermitted%2DCross%2DDomain%2DPolicies%20%C2%B7%20X%2D

using System.Threading.Tasks;
using FinsProvisioning.Extensions;
using Microsoft.AspNetCore.Http;

namespace FinsProvisioning.Middleware
{
  public class SecurityHeadersMiddleware
  {
    private readonly RequestDelegate _next;

    public SecurityHeadersMiddleware(RequestDelegate next)
    {
      _next = next;
    }

    public Task Invoke(HttpContext httpContext)
    {
      httpContext.Response.Headers.UpsertHeader("X-Frame-Options", "DENY");
      httpContext.Response.Headers.UpsertHeader("X-XSS-Protection", "1; mode=block");
      httpContext.Response.Headers.UpsertHeader("X-Content-Type-Options", "nosniff");
      httpContext.Response.Headers.UpsertHeader("Referrer-Policy", "no-referrer");
      httpContext.Response.Headers.UpsertHeader("X-Permitted-Cross-Domain-Policies", "none");
      httpContext.Response.Headers.UpsertHeader("Permissions-Policy", "accelerometer 'none'; camera 'none'; geolocation 'none'; gyroscope 'none'; magnetometer 'none'; microphone 'none'; payment 'none'; usb 'none'");
      httpContext.Response.Headers.UpsertHeader("Content-Security-Policy", "form-action 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'");

      return _next.Invoke(httpContext);
    }
  }
}

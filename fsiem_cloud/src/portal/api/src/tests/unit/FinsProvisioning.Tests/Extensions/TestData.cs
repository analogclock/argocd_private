using System;
using System.Collections.Generic;
using FortinetOne.Client.Model.Responses;

namespace FinsProvisioning.Tests.Extensions
{
  public class TestData
  {
    public static FoFortiSIEMCloudResponse CreateAPIResponse(string serial, DateTimeOffset? endDate = null)
    {
      return new FoFortiSIEMCloudResponse
      {
        Data = new List<FoFortiSIEMCloudResponseData>
        {
          new FoFortiSIEMCloudResponseData
          {
            SerialNumber = serial,
            Description = "FortiSIEM Test Evaluation",
            Entitlements = new List<Term>()
            {
              new Term()
              {
                EndDate = endDate ?? DateTimeOffset.UtcNow.AddDays(7),
                StartDate = DateTimeOffset.UtcNow,
                SupportType = 224,
                SupportTypeDescription = "FSM Compute",
                SupportLevel = 6,
                SupportLevelDescription = "Web/Online",
                Quantity = 10
              },
              new Term()
              {
                EndDate = endDate ?? DateTimeOffset.UtcNow.AddYears(1),
                StartDate = DateTimeOffset.UtcNow,
                SupportType = 225,
                SupportTypeDescription = "FSM Online Storage",
                SupportLevel = 6,
                SupportLevelDescription = "Web/Online",
                Quantity = 1
              },
              new Term()
              {
                EndDate = endDate ?? DateTimeOffset.UtcNow.AddYears(1),
                StartDate = DateTimeOffset.UtcNow,
                SupportType = 226,
                SupportTypeDescription = "FSM Archive Storage",
                SupportLevel = 6,
                SupportLevelDescription = "Web/Online",
                Quantity = 1
              }
            }
          },
          new FoFortiSIEMCloudResponseData
          {
              Description = "FortiSIEM Test Evaluation",
              Entitlements = new List<Term>()
              {
                new Term()
                {
                  EndDate = endDate ?? DateTimeOffset.UtcNow.AddYears(1),
                  StartDate = DateTimeOffset.UtcNow,
                  SupportType = 224,
                  SupportTypeDescription = "FSM Compute",
                  SupportLevel = 6,
                  SupportLevelDescription = "Web/Online",
                  Quantity = 5
                },
                new Term()
                {
                  EndDate = endDate ?? DateTimeOffset.UtcNow.AddYears(1),
                  StartDate = DateTimeOffset.UtcNow,
                  SupportType = 225,
                  SupportTypeDescription = "FSM Online Storage",
                  SupportLevel = 6,
                  SupportLevelDescription = "Web/Online",
                  Quantity = 1
                },
                new Term()
                {
                  EndDate = endDate ?? DateTimeOffset.UtcNow.AddYears(1),
                  StartDate = DateTimeOffset.UtcNow,
                  SupportType = 226,
                  SupportTypeDescription = "FSM Archive Storage",
                  SupportLevel = 6,
                  SupportLevelDescription = "Web/Online",
                  Quantity = 1
                }
              }
          }
        }
      };
    }
  }
}

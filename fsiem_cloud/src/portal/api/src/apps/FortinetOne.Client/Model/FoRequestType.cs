namespace FortinetOne.Client.Model
{
  public class FoRequestType
  {
    public static string GetCommonSettingRequest = "FortinetOneAPI.CommonService.GetCommonSettingRequest";
    public static string GetPortalListRequest = "FortinetOneAPI.CommonService.GetPortalListRequest";
    public static string GetLoginAccountsByEmailRequest = "FortinetOneAPI.IdentityService.GetLoginAccountsByEmailRequest";
    public static string GetAccountDetailsRequest = "FortinetOneAPI.IdentityService.GetAccountDetailsRequest";
    public static string GetProductListRequest = "FortinetOneAPI.ProductService.GetProductListRequest";
    public static string GetProductEntitlementListRequest = "FortinetOneAPI.ProductService.GetProductEntitlementListRequest";
    public static string GetProductSupportQuantityRequest = "FortinetOneAPI.ProductService.GetProductSupportQuantityRequest";
    public static string GetLicenseListRequest = "FortinetOneAPI.ProductService.GetLicenseListRequest";
    public static string RegisterLicenseRequest = "FortinetOneAPI.ProductService.RegisterLicenseRequest";
    public static string GetLicenseDetailsRequest = "FortinetOneAPI.ProductService.GetLicenseDetailsRequest";
    public static string GetProductKeysRequest = "FortinetOneAPI.ProductService.GetProductKeysRequest";
    public static string GetUserPortalAccessPermissionRequest = "FortinetOneAPI.SecurityService.GetUserPortalAccessPermissionRequest";

    // v3 payload requests
    public static string FortiSIEMCloudGetProductEntitlementsPayload = "FortinetOne.API.V3.FortiSIEMCloud.GetProductEntitlementsPayload";
    public static string FortiSIEMCloudGetProductEntitlementsBySerialNumberPayload = "FortinetOne.API.V3.FortiSIEMCloud.GetProductEntitlementsBySerialNumberPayload";
    public static string GetLicenseKeyPayload = "FortinetOne.API.V3.FortiSIEMCloud.GetLicenseKeyPayload";
    public static string GetPortalListPayload = "FortinetOne.API.V3.Common.GetPortalListPayload";
    public static string GetUserPermissionsPayload = "FortinetOne.API.V3.Common.GetUserPermissionsPayload";
    public static string GetAPIUserPermissionsPayload = "FortinetOne.API.V3.Common.GetAPIUserPermissionPayload";
    public static string GetFortiCloudLogoPayload = "FortinetOne.API.V3.Common.GetFortiCloudLogoPayload";
    public static string GetFortiCloudPremiumSubscriptionPayload = "FortinetOne.API.V3.Common.GetFortiCloudPremiumSubscriptionPayload";
    public static string GetAccountsByEmailPayload = "FortinetOne.API.V3.Common.GetAccountsByEmailPayload";
    public static string GetAccountDetailsPayload = "FortinetOne.API.V3.Common.GetAccountDetailsPayload";
    public static string GetCommonDataPayload = "FortinetOne.API.V3.Common.GetCommonDataPayload";
    public static string GetCommonDataLastUpdatePayload = "FortinetOne.API.V3.Common.GetCommonDataLastUpdatedTimePayload";
  }
}

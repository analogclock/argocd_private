using Newtonsoft.Json;

namespace FortinetOne.Client.Model.Responses
{
  public class FoGetFortiCloudLogoResponse : FoResponseV3<FoGetFortiCloudLogo>
  {
  }

  public class FoGetFortiCloudLogo
  {
    //{
    //    "hasPremiumSubscription": true,
    //    "logo_id": "id of logo"
    //}
    [JsonProperty("hasPremiumSubscription")]
    public bool? HasPremiumSubscription { get; set; } = null;

    [JsonProperty("logo_id")]
    public int LogoId { get; set; } = 0;

    public FoGetFortiCloudLogo()
    {
    }
  }
}

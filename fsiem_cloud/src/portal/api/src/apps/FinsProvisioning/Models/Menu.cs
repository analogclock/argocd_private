using System.Collections.Generic;

namespace FinsProvisioning.Models
{
  public class Menu
  {
    public List<CommonPortalItem> PortalMenuItems { get; set; }

    public List<CommonHeaders> PortalMenuHeaders { get; set; }

    public List<CommonMenuItem> UserMenuItems { get; set; }

    public List<CommonHeaders> SupportMenuHeaders { get; set; }

    public List<CommonMenuItem> SupportMenuItems { get; set; }

    public List<CommonConfigurations> Configurations { get; set; }

    public List<CommonLogosItem> Logos { get; set; }

    public Menu()
    {
    }
  }

  public class CommonConfigurations
  {
    public string Name { get; set; }

    public string Value { get; set; }
  }

  public class CommonItemImage
  {
    public int Order { get; set; }

    public string ImageContent { get; set; }
  }

  public class CommonItem : CommonItemImage
  {
    public string DisplayName { get; set; }

    public string Description { get; set; }

    public string Url { get; set; }

    public string SectionHeader { get; set; }
  }

  public class CommonPortalItem : CommonItem
  {
    public int ItemId { get; set; }

    public string AppName { get; set; }
  }

  public class CommonMenuItem : CommonItem
  {
    public int ItemId { get; set; }
  }

  public class CommonLogosItem : CommonItemImage
  {
    public int LogoId { get; set; }
  }

  public class CommonHeaders
  {
    public string DisplayName { get; set; }

    public string Description { get; set; }

    public string Url { get; set; }

    public int Order { get; set; }
  }
}

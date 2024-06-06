using Newtonsoft.Json;
using Newtonsoft.Json.Serialization;

namespace FinsProvisioning.Extensions
{
  public static class JsonEx
  {
    /// <summary>
    /// Deserialize JSON string with provided settings
    /// </summary>
    /// <typeparam name="T">Type to Deserialize into</typeparam>
    /// <param name="json">JSON string to Deserialize</param>
    /// <param name="settings">JSON settings to provide</param>
    /// <returns></returns>
    public static T Deserialize<T>(this string json, JsonSerializerSettings settings = null)
    {
      if (settings != null)
      {
        return JsonConvert.DeserializeObject<T>(json, settings);
      }

      return JsonConvert.DeserializeObject<T>(json);
    }

    /// <summary>
    /// Deserialize JSON string with default camel case settings
    /// </summary>
    /// <typeparam name="T">Type to Deserialize into</typeparam>
    /// <param name="json">JSON string to Deserialize</param>
    /// <returns></returns>
    public static T DeserializeCamel<T>(this string json)
    {
      return json.Deserialize<T>(
        new JsonSerializerSettings()
        {
          ContractResolver = new CamelCasePropertyNamesContractResolver(),
          NullValueHandling = NullValueHandling.Ignore
        }
      );
    }

    public static string Serialize<T>(this T obj, JsonSerializerSettings settings = null) where T : class
    {
      if (settings == null)
        return JsonConvert.SerializeObject(obj);

      return JsonConvert.SerializeObject(obj, settings);
    }

    public static string SerializeCamel<T>(this T obj) where T : class
    {
      return obj.Serialize(
        new JsonSerializerSettings()
        {
          ContractResolver = new CamelCasePropertyNamesContractResolver(),
          NullValueHandling = NullValueHandling.Ignore
        });
    }
  }
}

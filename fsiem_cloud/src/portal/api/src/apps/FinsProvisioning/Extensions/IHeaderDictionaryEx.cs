using Microsoft.AspNetCore.Http;

namespace FinsProvisioning.Extensions
{
  public static class IHeaderDictionaryEx
  {
    /// <summary>
    /// Add header by key if it doesn't already exist
    /// </summary>
    /// <param name="dictionary">Headers dictionary to add to</param>
    /// <param name="key">key to add to headers</param>
    /// <param name="value">value to add to header key</param>
    public static void UpsertHeader(this IHeaderDictionary dictionary, string key, string value)
    {
      if (!dictionary.ContainsKey(key))
      {
        dictionary.Append(key, value);
      }
    }
  }
}

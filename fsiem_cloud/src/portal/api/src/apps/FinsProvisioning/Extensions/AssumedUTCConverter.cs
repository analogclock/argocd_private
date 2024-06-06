using System;
using Newtonsoft.Json;

namespace FinsProvisioning.Extensions
{
  public class AssumedUTCConverter : JsonConverter
  {
    public override bool CanConvert(Type objectType)
    {
      return objectType == typeof(DateTimeOffset);
    }

    public override object ReadJson(JsonReader reader, Type objectType, object existingValue, JsonSerializer serializer)
    {
      if (reader.Value == null)
        return null;

      try
      {
        // 2024-03-11T18:18:17 - example of python date
        var dt = (DateTime)reader.Value;
        return new DateTimeOffset(dt, new TimeSpan(0));
      }
      catch
      { }

      // not much we can do at this stage
      return null;

    }

    public override void WriteJson(JsonWriter writer, object value, JsonSerializer serializer)
    {
      writer.WriteValue(value);
    }
  }
}

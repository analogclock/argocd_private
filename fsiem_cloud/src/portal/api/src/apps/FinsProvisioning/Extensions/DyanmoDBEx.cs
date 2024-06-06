using System.Collections.Generic;
using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.DocumentModel;
using Amazon.DynamoDBv2.Model;

namespace FinsProvisioning.Extensions
{
  public static class DynamoDBExtensions
  {
    public static Document ToDynamoDBDoc<T>(this T obj) where T : class
    {
      if (obj == null)
        return null;

      return Document.FromJson(obj.SerializeCamel());
    }

    public static AttributeValueUpdate ToChange(this string value)
    {
      return new AttributeValueUpdate
      {
        Action = AttributeAction.PUT,
        Value = new AttributeValue { S = value }
      };
    }

    public static AttributeValueUpdate ToChange<T>(this T value) where T : class
    {
      var doc = value.ToDynamoDBDoc();
      return new AttributeValueUpdate
      {
        Action = AttributeAction.PUT,
        Value = new AttributeValue { M = doc.ToAttributeMap() }
      };
    }

    public static void AddChange(this Dictionary<string, AttributeValueUpdate> updates, string key, string value)
    {
      if (!string.IsNullOrWhiteSpace(key) && value != null)
      {
        updates[key] = value.ToChange();
      }
    }
  }
}

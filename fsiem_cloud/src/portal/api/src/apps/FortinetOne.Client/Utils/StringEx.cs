namespace FortinetOne.Client.Utils
{
  public static class StringEx
  {
    // based on https://stackoverflow.com/a/1476563/706456
    // There's no easy way to combine two URI if the first one has a slash. 
    // See SO comment to this answer https://stackoverflow.com/a/372888/706456
    //
    //      "This answer suffers the same problem as Joel's:
    //      joining test.com/mydirectory/ and /helloworld.aspx
    //      will result in test.com/helloworld.aspx"
    //
    public static string UriCombine(this string uri1, string uri2)
    {
      uri1 = uri1.TrimEnd('/');
      uri2 = uri2.TrimStart('/');
      return $"{uri1}/{uri2}";
    }
  }
}

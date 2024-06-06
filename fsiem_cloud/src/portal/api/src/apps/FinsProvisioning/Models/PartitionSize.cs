using System;
using System.Collections.Generic;
using System.Globalization;

/// <summary>
/// A data transfer object as it's stored in this DynamoDb table
/// fsiem_metrics_storage_env. It corresponds to a single row in the table.
/// </summary>
public class PartitionSizeDto
{
  /// <summary>
  /// SN, e.g. FSMCLD0000000182
  /// </summary>
  public string SerialNumber { get; set; }

  /// <summary>
  /// Utc date time, e.g. 2024-02-08T21:34:19.078676
  /// </summary>
  public string LastUpdated { get; set; }

  /// <summary>
  /// A base64 string of the compressed bytes for online storage
  /// </summary>
  public string OnlineGzip { get; set; }

  /// <summary>
  /// A base64 string of the compressed bytes for archive storage
  /// </summary>
  public string ArchiveGzip { get; set; }
}

/// <summary>
/// A single item of the partition metric, this is what stored inside the
/// compressed array of online/archive metrics.
/// </summary>
public class PartitionSizeStatDto
{
  /// <summary>
  /// Date in this format: 20240208
  /// </summary>
  public string d { get; set; }

  /// <summary>
  /// Number of rows stored in Clickhouse for this partition/day, e.g. 113008
  /// </summary>
  public string r { get; set; }

  /// <summary>
  /// Number of bytes for this partition/day stored on disk in compressed form, e.g. 1479004
  /// </summary>
  public string b { get; set; }

  /// <summary>
  /// An average of bytes stored on disk in compressed form for this partition, e.g 1479004.0
  /// </summary>
  public double aB { get; set; }

  /// <summary>
  /// Number of decompressed bytes for this partition/day, e.g. 1479004
  /// </summary>
  public string uB { get; set; }

  /// <summary>
  /// An average of decompressed bytes for this partition, e.g 1479004.0
  /// </summary>
  public double aUB { get; set; }

  /// <summary>
  /// Convert DTO to an object with better names
  /// </summary>
  public PartitionSizeStat ToPartitionSizeStatItem()
  {
    return new PartitionSizeStat
    {
      Day = DateTimeOffset.ParseExact(d, "yyyyMMdd", CultureInfo.InvariantCulture, DateTimeStyles.AssumeUniversal),
      Rows = long.Parse(r),
      Bytes = long.Parse(b),
      AvgBytes = aB,
      UncompressedBytes = long.Parse(uB),
      AvgUncompressedBytes = aUB
    };
  }
}

/// <summary>
/// A single storage metric for one partition
/// </summary>
public class PartitionSizeStat
{
  public DateTimeOffset Day { get; set; }
  public long Rows { get; set; }
  public long Bytes { get; set; }
  public double AvgBytes { get; set; }
  public long UncompressedBytes { get; set; }
  public double AvgUncompressedBytes { get; set; }
}

/// <summary>
/// Metric that shows online and archive partitions with their stats: rows, bytes
/// </summary>
public class PartitionSize
{
  public string SerialNumber { get; set; }
  public string LastUpdated { get; set; }
  public List<PartitionSizeStat> Online { get; set; } = new List<PartitionSizeStat>();
  public List<PartitionSizeStat> Archive { get; set; } = new List<PartitionSizeStat>();

  public PartitionSize(
    string sn,
    string lastUpdated,
    List<PartitionSizeStatDto> online,
    List<PartitionSizeStatDto> archive)
  {
    SerialNumber = sn;
    LastUpdated = lastUpdated;
    Online = online.ConvertAll(x => x.ToPartitionSizeStatItem());
    Archive = archive.ConvertAll(x => x.ToPartitionSizeStatItem());
  }
}

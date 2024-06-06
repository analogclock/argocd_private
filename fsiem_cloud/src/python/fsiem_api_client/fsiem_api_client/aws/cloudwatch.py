import boto3
import concurrent.futures
from functools import partial
from datetime import datetime, timedelta


class CloudWatch:
    """A client class for AWS CloudWatch"""

    # From https://docs.aws.amazon.com/AmazonS3/latest/userguide/metrics-dimensions.html # noqa
    storage_types = [
        'StandardStorage', 'IntelligentTieringFAStorage',
        'IntelligentTieringIAStorage', 'IntelligentTieringAAStorage',
        'IntelligentTieringAIAStorage', 'IntelligentTieringDAAStorage',
        'StandardIAStorage', 'StandardIASizeOverhead',
        'StandardIAObjectOverhead', 'OneZoneIAStorage',
        'OneZoneIASizeOverhead', 'ReducedRedundancyStorage',
        'GlacierInstantRetrievalSizeOverhead',
        'GlacierInstantRetrievalStorage', 'GlacierStorage',
        'GlacierStagingStorage', 'GlacierObjectOverhead',
        'GlacierS3ObjectOverhead', 'DeepArchiveStorage',
        'DeepArchiveObjectOverhead', 'DeepArchiveS3ObjectOverhead',
        'DeepArchiveStagingStorage'
    ]

    def __init__(self, region: str) -> None:
        self.client = boto3.client('cloudwatch', region_name=region)

    def s3_bucket_size(self, s3_bucket: str) -> int:
        """Get the size of S3 bucket for the previous day, all objects inside
        it, and all versions, across all different storage types. This method
        runs multiple queries in parallel"""
        if not s3_bucket:
            raise ValueError('s3_bucket not provided')

        total_size = 0
        # Run queries concurrently in a threadpool
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # executor.map call requires 2 arguments - function name and an
            # iterator that will be used for parallel execution as a single
            # arg. But our function takes in 2 arguments. To handle this, we
            # need to wrap the function into "partial", we can then pass
            # partial to map.
            # Based on https://stackoverflow.com/a/62552042/706456
            func_with_1arg = partial(
                self.s3_bucket_storage_type_size, s3_bucket)
            results = executor.map(func_with_1arg, self.storage_types)

            # Sum results, no longer parallel.
            # Result blocks when not available yet
            for result in results:
                total_size += result
        return total_size

    def s3_bucket_storage_type_size(self, s3_bucket: str,
                                    storage_type='StandardStorage') -> int:
        """Get the size of S3 bucket for the previous day, all objects inside it,
        and all versions.
        See https://docs.aws.amazon.com/AmazonS3/latest/userguide/cloudwatch-monitoring-accessing.html # noqa

        S3_BUCKET=forticwpbucket08ed894b-8a42-477b-81b6-4f16c8b4dfd4
        aws cloudwatch get-metric-statistics --metric-name BucketSizeBytes    \
            --namespace AWS/S3 --statistics Average --unit Bytes              \
            --start-time 2022-10-25T00:00:00Z --end-time 2022-10-26T00:00:00Z \
            --period 86400 --output json                                      \
            --dimensions Name=BucketName,Value=$S3_BUCKET                     \
                        Name=StorageType,Value=StandardStorage

        Parameters
        ----------
        s3_bucket : str
            S3 bucket name
        storage_type: str
            S3 storage type (there are quite a few). We cannot aggregate by all
            types with AWS CloudWatch API. The returns empty response.

        Returns
        -------
        int
            Size of the bucket in bytes, calculated for the previous day.
        """
        if not s3_bucket:
            raise ValueError('s3_bucket not provided')
        if not storage_type:
            raise ValueError('storage_type not provided')

        try:
            midnight = datetime.now().replace(hour=0, minute=0, second=0)

            r = self.client.get_metric_statistics(
                Namespace='AWS/S3',
                MetricName='BucketSizeBytes',
                Dimensions=[
                    {'Name': 'BucketName', 'Value': s3_bucket},
                    {'Name': 'StorageType', 'Value': storage_type},
                ],
                StartTime=midnight - timedelta(days=2),
                EndTime=midnight - timedelta(days=1),
                Period=86400,
                Statistics=['Average'],
                Unit='Bytes'
            )
            data = r['Datapoints']
            size = int(data[0]['Average']) if len(data) > 0 else 0
            print(f'S3 bucket "{s3_bucket}" [{storage_type}]: {size} bytes')
            return size
        except Exception as e:
            print(f'Failed to get size of S3 bucket {s3_bucket}')
            print(e)
            return 0

    def s3_bucket_object_count(self, s3_bucket: str,
                               storage_type='AllStorageTypes') -> int:
        """Get the number of objects in bucket for the previous day,
        all objects inside it, and all versions.
        See https://docs.aws.amazon.com/AmazonS3/latest/userguide/cloudwatch-monitoring-accessing.html # noqa

        S3_BUCKET=forticwpbucket08ed894b-8a42-477b-81b6-4f16c8b4dfd4
        aws cloudwatch get-metric-statistics --metric-name NumberOfObjects    \
            --namespace AWS/S3 --statistics Average --unit Count              \
            --start-time 2022-10-25T00:00:00Z --end-time 2022-10-26T00:00:00Z \
            --period 86400 --output json                                      \
            --dimensions Name=BucketName,Value=$S3_BUCKET                     \
                        Name=StorageType,Value=AllStorageTypes

        Parameters
        ----------
        s3_bucket : str
            S3 bucket name
        storage_type: str
            S3 storage type, defaults to AllStorageTypes (we can use it here).

        Returns
        -------
        int
            Number of objects, calculated for the previous day.
        """
        if not s3_bucket:
            raise ValueError('s3_bucket not provided')
        if not storage_type:
            raise ValueError('storage_type not provided')

        try:
            midnight = datetime.now().replace(hour=0, minute=0, second=0)
            r = self.client.get_metric_statistics(
                Namespace='AWS/S3',
                MetricName='NumberOfObjects',
                Dimensions=[
                    {'Name': 'BucketName', 'Value': s3_bucket},
                    {'Name': 'StorageType', 'Value': storage_type},
                ],
                Unit='Count',
                StartTime=midnight - timedelta(days=2),
                EndTime=midnight - timedelta(days=1),
                Period=86400,
                Statistics=['Average'],
            )
            data = r['Datapoints']
            size = int(data[0]['Average']) if len(data) > 0 else 0
            print(f'S3 bucket "{s3_bucket}" [{storage_type}]: {size} objects')
            return size
        except Exception as e:
            print(f'Failed to get number of objects for S3 bucket {s3_bucket}')
            print(e)
            return 0

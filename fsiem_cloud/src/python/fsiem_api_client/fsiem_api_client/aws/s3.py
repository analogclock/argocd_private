import boto3
import time
from botocore.exceptions import ClientError
from smart_open import open
from fsiem_api_client.deployment_metrics import DeploymentMetrics
from fsiem_api_client.extensions import chunk


class S3:
    """A client class for AWS S3"""

    def __init__(self, region: str) -> None:
        self.s3 = boto3.resource('s3', region_name=region)
        self.client = boto3.client('s3', region_name=region)
        self.control_client = boto3.client('s3control', region_name=region)

    def list_buckets(self):
        """Returns a collection of all S3 buckets"""
        return self.s3.buckets.all()

    def list_versions(self, s3_bucket: str, inc_latest: bool):
        """List metadata for versioned objects in an S3 bucket

        Parameters
        ----------
        s3_bucket : str
            S3 bucket name
        inc_latest : bool
            Shall the query return the latest version or not.
            When False - only stale versions will be returned
            When True - stale and current versions will be returned

        Returns
        -------
            Version object metadata
        """
        all = self.s3.Bucket(s3_bucket).object_versions.all()
        return all if inc_latest else filter(lambda x: not x.is_latest, all)

    def delete_objects(self, s3_bucket: str, objects):
        """Delete objects versions in the S3 buckets.

        Use this method with list_versions to get the
        objects needed for deletion.

        Parameters
        ----------
        s3_bucket : str
            S3 bucket name
        objects :
            An iterable collection of metadata for the objects to be removed.
            This must include key and version_id.
        """
        pages = chunk(objects, 1000)
        for page in pages:
            resp = self.s3.Bucket(s3_bucket).delete_objects(
                Delete={
                    'Objects': [{
                        'Key': item.key,
                        'VersionId': item.version_id
                    } for item in page]
                })
            print(resp)

    def s3_dir_metrics(self, s3_bucket: str, dir: str) -> DeploymentMetrics:
        """Get metrics for S3 bucket and dir inside that bucket"""
        if not s3_bucket:
            raise ValueError('s3_bucket not provided')
        if not dir:
            raise ValueError('dir not provided')

        metric = DeploymentMetrics(
            s3_archive_bucket=s3_bucket,
            s3_archive_dir=dir)

        for item in self.s3.Bucket(s3_bucket).objects.filter(Prefix=dir):
            metric.s3_archive_size_bytes += item.size
            metric.s3_archive_objects_count += 1

        return metric

    def enumerate_object_keys(self, bucket: str, prefix: str,
                              date_modified_before=None,
                              date_modified_after=None,
                              **kwargs):
        """Enumerate keys and last modified date in a bucket, usually in small
           batches of 1000 items by default

        Parameters
        ----------
        bucket : str
            S3 bucket name
        prefix : str
            Any prefix for the key
        date_modified_before : datetime, optional
            Only get keys that are older than this datetime, by default None
        date_modified_after : datetime, optional
            Only get keys that are newer than this datetime, by default None
        kwargs: dict
            Any additional argument(s) that S3 API supports, e.g. MaxKeys
        Returns
        -------
        enumerable
            A list of keys in batches, use with for loop

            for items in self.enumerate_object_keys(...)

                # items look like
                [
                    'FSMCLD0000000177/10.0.101.215/aa',
                    'FSMCLD0000000177/10.0.101.215/bb'
                ]
        """
        print(f'Getting keys in {bucket}/{prefix}')
        print(f'Server side filtering by prefix: {prefix}')
        if date_modified_before:
            print(f"Client filtering, modified before: {date_modified_before}")

        if date_modified_after:
            print(f"Client filtering, modified after: {date_modified_after}")

        # This dictionary is passed to S3 API: list_objects_v2(args)
        args = {}
        args["Bucket"] = bucket
        args["Prefix"] = prefix
        args.update(kwargs)

        # Count all objects in the bucket/prefix
        total = 0
        # If using client side filtering, this will show how many was retained
        # after applying filters like date_modified_before
        enumerated = 0

        # A pointer to get the next batch of object
        continuation_token = None

        while True:
            keys = []

            if continuation_token:
                args["ContinuationToken"] = continuation_token

            resp = self.client.list_objects_v2(**args)

            # Iterate over 1 batch, usually 1k objects, set by MaxKeys
            for item in resp.get("Contents", []):
                total += 1
                if (
                    date_modified_before
                    and not item["LastModified"] < date_modified_before
                ):
                    continue

                if (
                    date_modified_after
                    and not item["LastModified"] > date_modified_after
                ):
                    continue

                enumerated += 1
                keys.append(item["Key"])

            # return one batch now
            if keys:
                yield keys

            # If more than 1k objects, continue with token
            if resp.get("NextContinuationToken"):
                continuation_token = resp["NextContinuationToken"]
            else:
                # nothing else left and we've returned previous batch
                print(f'''
                      Enumeration of keys finished, returned {enumerated}
                      keys, out of {total} scanned keys
                      ''')
                break

    def enumerate_job_manifest(self, bucket: str, prefix: str,
                               date_modified_before=None,
                               date_modified_after=None,
                               **kwargs):
        """Create a multiline enumeration of strings for S3 job manifest file.
        Example is:

        <bucket>,<key1>
        <bucket>,<key2>
        ...

        Parameters
        ----------
        bucket : str
            S3 bucket name
        prefix : str
            Any prefix for the key
        date_modified_before : datetime, optional
            Only get keys that are older than this datetime, by default None
        date_modified_after : datetime, optional
            Only get keys that are newer than this datetime, by default None
        kwargs: dict
            Any additional argument(s) that S3 API supports, e.g. MaxKeys

        Returns
        -------
        enumerable str
            A string to write into the manifest file, in batches of 1k entries
            by default

            for items in enumerate_job_manifest(...)
                # items look like
                'fsiem-clickhouse-data-us-east-1-dev,FSMCLD0000000177/10.0.101.215/aabebajxrzvghpspvzznppmfildkfxen\n...'

        """
        for items in self.enumerate_object_keys(bucket,
                                                prefix,
                                                date_modified_before,
                                                date_modified_after,
                                                **kwargs):
            yield [f'{bucket},{key}\n' for key in items]

    def upload_job_manifest(self,
                            manifest_bucket: str,
                            manifest_key: str,
                            manifest_tags: str,
                            bucket: str, prefix: str,
                            date_modified_before=None,
                            date_modified_after=None,
                            **kwargs) -> dict[str, str]:
        """Create and upload manifest file for S3 jobs. Manifest file is a csv
        file with bucket name and key of the object.

        Parameters
        ----------
        manifest_bucket : str
            Bucket where manifest file will be stored
        manifest_key : str
            The key of the manifest file, e.g. manifests/SerialNumber123.csv
        manifest_tags : str
            Tags in UTF8 + UrlEncoded format, e.g.: key1=value1&key2=value2
        bucket : str
            S3 bucket name
        prefix : str
            Any prefix for the key
        date_modified_before : datetime, optional
            Only get keys that are older than this datetime, by default None
        date_modified_after : datetime, optional
            Only get keys that are newer than this datetime, by default None
        kwargs: dict
            Any additional argument(s) that S3 API supports, e.g. MaxKeys

        Returns
        -------
        dict[str, str]
            A dictionary with Arn and ETag of the resource, for example
            {
                'Arn': 's3://fsiem-clickhouse-.../manifests/1.csv',
                'ETag': '9234260e7a617ac1ac66a1b618bb117b-1'
            }
        """
        tp = {
            'client': self.client,
            'client_kwargs': {
                'S3.Client.create_multipart_upload': {
                    'Tagging': manifest_tags,
                    'ContentType': 'text/csv'
                }
            }
        }
        out_uri = f's3://{manifest_bucket}/{manifest_key}'

        print(f'Uploading {out_uri}')
        with open(out_uri, 'wt', transport_params=tp) as out:
            for lines in self.enumerate_job_manifest(bucket,
                                                     prefix,
                                                     date_modified_before,
                                                     date_modified_after,
                                                     **kwargs):
                out.writelines(lines)

        print('Retrieving ETag of the manifest file')
        resp = self.client.get_object_attributes(
            Bucket=manifest_bucket,
            Key=manifest_key,
            ObjectAttributes=['ETag'])

        return {
            'Arn': f'arn:aws:s3:::{manifest_bucket}/{manifest_key}',
            'ETag': resp["ETag"]
        }

    def create_s3_tagging_job(self,
                              account_id: str,
                              role_arn: str,
                              manifest_bucket: str,
                              manifest_key: str,
                              manifest_tags: str,
                              bucket: str,
                              prefix: str,
                              object_tags: list[dict[str, str]],
                              date_modified_before=None,
                              date_modified_after=None,
                              **kwargs) -> str:
        """Create a job that tags objects in S3 bucket

        Parameters
        ----------
        account_id : str
            AWS account that runs the job
        role_arn : str
            ARN of the role that runs the job
        manifest_bucket : str
            Bucket where manifest file will be stored
        manifest_key : str
            The key of the manifest file, e.g. manifests/SerialNumber123.csv
        manifest_tags : str
            Tags in UTF8 + UrlEncoded format, e.g.: key1=value1&key2=value2
        bucket : str
            S3 bucket name
        prefix : str
            Any prefix for the key, e.g. serial number
        object_tags : list[dict[str, str]]
            Tag set, for example [{'Key': 'SerialNumber', 'Value': '123'}]
        date_modified_before : datetime, optional
            Only get keys that are older than this datetime, by default None
        date_modified_after : datetime, optional
            Only get keys that are newer than this datetime, by default None
        kwargs: dict
            Any additional argument(s) that S3 API supports, e.g. MaxKeys

        Returns
        -------
        str
            Job id
        """
        resp = self.upload_job_manifest(manifest_bucket,
                                        manifest_key,
                                        manifest_tags,
                                        bucket,
                                        prefix,
                                        date_modified_before,
                                        date_modified_after,
                                        **kwargs)
        manifest_arn = resp['Arn']
        manifest_etag = resp['ETag']
        print(f'Manifest created, arn: {manifest_arn}, etag; {manifest_etag}')

        print(f'Creating S3 job to tag {bucket}/{prefix} objects')
        print(f'Will apply (replace) these tags: {str(object_tags)}')
        response = self.control_client.create_job(
            AccountId=account_id,
            RoleArn=role_arn,
            Description=f'Tag {bucket}/{prefix} objects',
            Report={
                'Enabled': False
            },
            Manifest={
                'Spec': {
                    'Format': 'S3BatchOperations_CSV_20180820',
                    'Fields': ['Bucket', 'Key']
                },
                'Location': {
                    'ObjectArn': manifest_arn,
                    'ETag': manifest_etag
                }
            },
            Priority=1,
            Operation={
                'S3PutObjectTagging': {
                    'TagSet': object_tags
                }
            }
        )

        job_id = response['JobId']
        print(f'Job id: {job_id}')

        # Note 1: when we create a job, it is created with a status
        # "awaiting your confirmation to run". To run the job
        # we need to update its status.
        #
        # Note 2: We need to wait a little before calling update_job_status
        # API. If we make a call to update the job immediately, we will get
        # "An error occurred (InvalidRequest) when calling the
        # UpdateJobStatus operation: Requested job status forbidden."
        # It seems AWS needs a couple of seconds before the job can be updated.
        #
        print('Trying to update job status. The call may '
              'fail if the job creation is not finalized')
        print('Expect a couple of these: Requested job status forbidden')
        for i in range(1, 11):
            try:
                print(f'Attempt: {i}')
                return self.control_client.update_job_status(
                    AccountId=account_id,
                    JobId=job_id,
                    RequestedJobStatus='Ready')
            except ClientError as err:
                print(f"Client error: {err}")
                # failed to update, let's retry in "i" seconds: 1, 2, ..., 10
                time.sleep(i)
                continue

        print('ERROR: All attempts to run the job failed')
        raise ValueError(f"Failed to update job status to ready, id {job_id} ")

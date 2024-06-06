from fsiem_api_client.aws.s3 import S3

uut = S3(region='us-east-1')
s3_bucket = 'fsiem-clickhouse-data-us-east-1-dev'
sn = 'FSMCLD0000000177'


class TestS3:

    def test_s3_dir_metrics(self):
        actual = uut.s3_dir_metrics(s3_bucket, sn)
        assert actual.s3_archive_size_bytes > 0
        assert actual.s3_archive_objects_count > 0

        actual = uut.s3_dir_metrics(s3_bucket, 'dir-does-not-exist')
        assert actual.s3_archive_size_bytes == 0
        assert actual.s3_archive_objects_count == 0

    def test_delete_non_current_objects(self):
        items = uut.list_versions(s3_bucket, inc_latest=False)
        uut.delete_objects(s3_bucket, items)

    def test_delete_non_current_objects_clickhouse_buckets(self):
        buckets = filter(lambda x: x.name.startswith('fsiem-clickhouse-data'),
                         uut.list_buckets())
        for bucket in buckets:
            try:
                items = uut.list_versions(bucket.name, inc_latest=False)
                uut.delete_objects(s3_bucket, items)
            except Exception as err:
                print(err)

    def test_enumerate_object_keys(self):
        args = {'MaxKeys': 100}
        for items in uut.enumerate_object_keys(s3_bucket, sn, **args):
            assert items

    def test_create_job_manifest(self):
        for x in uut.enumerate_job_manifest(s3_bucket, sn):
            assert x

    def test_upload_job_manifest(self):
        args = {'MaxKeys': 100}
        tags = f'SerialNumber={sn}'
        resp = uut.upload_job_manifest(s3_bucket, f'manifests/{sn}.csv',
                                       tags, s3_bucket, sn, **args)
        assert resp

    def test_create_s3_tagging_job(self):
        args = {'MaxKeys': 100}
        manifest_tags = f'SerialNumber={sn}'
        object_tags = [{'Key': 'SerialNumber', 'Value': sn}]
        account_id = '023941436530'
        role_arn = 'not implemented yet'
        resp = uut.create_s3_tagging_job(
            account_id,
            role_arn,
            s3_bucket,
            f'manifests/{sn}.csv',
            manifest_tags,
            s3_bucket,
            sn,
            object_tags,
            **args)
        assert resp

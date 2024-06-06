from fsiem_api_client.aws.cloudwatch import CloudWatch


class TestCloudWatch:

    uut = CloudWatch(region='us-east-1')
    s3_bucket = 'forticwpbucket08ed894b-8a42-477b-81b6-4f16c8b4dfd4'

    def test_s3_bucket_storage_type_size(self):
        size = self.uut.s3_bucket_storage_type_size(
            self.s3_bucket, 'StandardStorage')
        assert size > 0
        size = self.uut.s3_bucket_storage_type_size(
            self.s3_bucket, 'DeepArchiveStagingStorage')
        assert size == 0

    def test_s3_bucket_size(self):
        size = self.uut.s3_bucket_size(self.s3_bucket)
        assert size > 0

    def test_s3_bucket_object_count(self):
        size = self.uut.s3_bucket_object_count(self.s3_bucket)
        assert size > 0

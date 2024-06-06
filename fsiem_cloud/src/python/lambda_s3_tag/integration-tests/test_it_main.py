
from fsiem_api_client.aws.s3 import S3
from fsiem_s3_tag.main import main


uut = S3(region='us-east-1')
s3_bucket = 'fsiem-clickhouse-data-us-east-1-dev'
sn = 'FSMCLD0000000177'


def test_create_s3_tagging_job(self):
    args = {'MaxKeys': 100}
    manifest_tags = f'SerialNumber={sn}'
    object_tags = [{'Key': 'SerialNumber', 'Value': sn}]
    account_id = '023941436530'
    role_arn = 'not implemented yet'
    main()
    resp = uut.create_s3_tagging_job(
        account_id,
        role_arn,
        sn,
        s3_bucket,
        f'manifests/{sn}.csv',
        manifest_tags,
        s3_bucket,
        sn,
        object_tags,
        **args)
    assert resp


from fsiem_api_client import ActivationTable
from job_tag_s3 import JobTagS3

lambda_region = 'us-east-1'
args = {
    "region": "eu-west-1",
    "sn": "FSMCLD0000000160",
    "account_id": "023941436530",
    "role_arn": "arn:aws:iam::023941436530:role/lambda-fsiem-s3-tag-playground", # noqa
    "manifest_bucket": "fsiem-s3-job-playground",
    "bucket": "fsiem-clickhouse-data-eu-west-1-playground",
    "prefix": "FSMCLD0000000160"
}

deployment = {
    "serialNumber": {"S": "FSMCLD0000000160"},
    "archiveSizeUsage": {"N": "0"},
    "created": {"S": "2023-06-20T18:36:38.3551302+00:00"},
    "deploymentEmail": {"S": "omandrychenko@fortinet.com"},
    "deploymentSKU": {
        "M": {
            "archiveStorage": {"M": {"quantity": {"N": "0"}}},
            "compute": {"M": {"endDate": {"S": "2023-08-09T00:00:00+00:00"},
                              "expiryDays": {"N": "50"},
                              "quantity": {"N": "11"},
                              "startDate": {"S": "2022-08-09T00:00:00+00:00"}
                              }
                        },
            "onlineStorage": {
                "M": {
                    "endDate": {"S": "2024-08-08T00:00:00+00:00"},
                    "expiryDays": {"N": "415"},
                    "quantity": {"N": "1"},
                    "startDate": {"S": "2022-08-09T00:00:00+00:00"}
                }
            }
        }
    },
    "deploymentType": {"S": "va"},
    "displayRegion": {"S": "Europe (Ireland)"},
    "fmonKey": {"S": "222"},
    "ipV4Cidr": {"S": "0.0.0.0/0"},
    "ipV6Cidr": {"S": "::/0"},
    "isPOC": {"BOOL": False},
    "onlineSizeUsage": {"N": "0"},
    "primaryAZ": {"S": "eu-west-1b"},
    "region": {"S": "eu-west-1"},
    "status": {"S": "CreateFailed"}
}


uut = JobTagS3(
    args["account_id"],
    lambda_region,
    "fsiem_s3_tag_playground",
    "arn:aws:iam::023941436530:role/lambda-fsiem-s3-tag-playground",
    "fsiem-s3-job-playground",
    "playground",
    "no-email-from",
    "no-email-to"
)


def test_invoke_async_s3_tag_lambda():
    resp = uut._invoke_async_s3_tag_lambda(args, None)
    assert resp


def test_run_s3_tag_task():
    uut._run_task(deployment, None)


def test_run_s3_tag_job():
    table = ActivationTable(
        'fsiem_activation_table_playground',
        'us-east-1')
    uut.run(table, None)


def test_ctor():
    uut = JobTagS3(
        args["account_id"],
        args["region"],
        "fsiem_s3_tag_dev",
        "arn:aws:iam::023941436530:role/lambda-fsiem-s3-tag-dev",
        "fsiem-s3-job-dev",
        "dev",
        "no-email-from",
        "no-email-to"
    )
    assert uut


def test_get_payload():
    j = uut._get_payload('eu-west-1', 'FSMCLD0000000160', 'data')
    assert j['region'] == 'eu-west-1'
    assert j['sn'] == 'FSMCLD0000000160'
    assert j['account_id'] == args["account_id"]
    assert j['role_arn'] == args["role_arn"]
    assert j['manifest_bucket'] == args["manifest_bucket"]
    assert j['bucket'] == args["bucket"]
    assert j['prefix'] == args["prefix"]

from fsiem_api_client.aws.s3 import S3


def main(event: dict, context):
    """AWS Lambda function that creates a job to tag S3 objects.

    The work looks like this:
    - scan S3 <bucket>/<prefix> for keys
    - save keys into a specially formatted CSV file in
      <manifest_bucket>/<manifest_key>
    - Create a job in S3 batch processing system to tag
      files using the manifest CSV file
    - Once job is created, trigger it to run

    Example event:

    {
        "region": "us-east-1",
        "sn": "FSMCLD0000000177",
        "account_id": "023941436530",
        "role_arn": "arn:aws:iam::<id>:role/lambda-fsiem-s3-tag-playground",
        "manifest_bucket": "fsiem-s3-job-playground",
        "manifest_tags": "SerialNumber=FSMCLD0000000177",
        "bucket": "fsiem-clickhouse-data-us-east-1-dev",
        "prefix": "FSMCLD0000000177"
    }

    Parameters
    ----------
    event : dict
        The event JSON object
        See: https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html
    context : Any
        Context information passed to the function at runtime.
        See: https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html
    """
    print('Executing S3 tagging lambda function')
    print(f'Received event: {event}')
    print(f'Received context: {str(context)}')

    s3 = S3(event['region'])
    manifest_key = f'manifests/s3-tag-job/{event["bucket"]}-{event["sn"]}.csv'
    object_tags = [{'Key': 'SerialNumber', 'Value': event['sn']}]
    print(f'Applying tags: {object_tags}')
    date_modified_before = None
    date_modified_after = None

    resp = s3.create_s3_tagging_job(
        event['account_id'],
        event['role_arn'],
        event['manifest_bucket'],
        manifest_key,
        event['manifest_tags'],
        event['bucket'],
        event['prefix'],
        object_tags,
        date_modified_before,
        date_modified_after,
    )
    print(f'Resp: {str(resp)}')

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": {
            "s3_tagging_job": resp
        }
    }

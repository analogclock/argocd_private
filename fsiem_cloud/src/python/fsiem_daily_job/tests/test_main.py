
from main import parse_args

args = {
    'aws_account_id': '023941436530',
    'dynamodb_region': 'us-east-1',
    'dynamodb_activation_table': 'fsiem_activation_table_playground',
    'lambda_region': 'us-east-1',
    's3_tag_lambda_name': 'fsiem_s3_tag_playground',
    's3_tag_lambda_role_arn': 'arn:aws:iam::023941436530:role/lambda-fsiem-s3-tag-playground', # noqa
    's3_manifest_bucket': 'fsiem-s3-job-playground',
    'environment': 'playground',
    'email_from_addr': 'no-email-from',
    'email_to_addr': 'no-email-to',
}


def test_parse_args():
    parser = parse_args([
        '--aws_account_id', args['aws_account_id'],
        '--dynamodb_region', args['dynamodb_region'],
        '--dynamodb_activation_table', args['dynamodb_activation_table'],
        '--lambda_region', args['lambda_region'],
        '--s3_tag_lambda_name', args['s3_tag_lambda_name'],
        '--s3_tag_lambda_role_arn', args['s3_tag_lambda_role_arn'],
        '--s3_manifest_bucket', args['s3_manifest_bucket'],
        '--environment', args['environment'],
        '--email_from_addr', args['email_from_addr'],
        '--email_to_addr', args['email_to_addr'],
        ])
    assert parser.aws_account_id == args['aws_account_id']

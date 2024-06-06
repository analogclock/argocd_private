import sys
from argparse import ArgumentParser
# from fsiem_api_client import ActivationTable
from fsiem_api_client.aws.ses import Ses
# from job_tag_s3 import JobTagS3


def main(options: dict):
    """Runs daily jobs"""
    # activation_table = ActivationTable(
    #     options['dynamodb_activation_table'],
    #     options['dynamodb_region'])

    # Ses requires some setup, we only did it for one region us-east-1
    ses = Ses('us-east-1')

    try:

        # Commented by OM on 22-Jan-2024. We used to tag every object in S3
        # with SerialNumber=<sn> tag, so we can calculate storage cost, per
        # stack. However, AWS Billing doesn't allow us to do so, it only
        # works with S3 Bucket level tagging. It cost about 1-2% to tag items,
        # and as it is not used, we want to disable tagging.

        # In the future we want to re-use this job to output cost metrics
        # in the other separate table.

        print("No work to do, exiting...")

        #
        #
        # Tag S3 objects
        #
        # job_s3_tag = JobTagS3(
        #     options["aws_account_id"],
        #     options["lambda_region"],
        #     options["s3_tag_lambda_name"],
        #     options["s3_tag_lambda_role_arn"],
        #     options["s3_manifest_bucket"],
        #     options["environment"],
        #     options["email_from_addr"],
        #     options["email_to_addr"])
        # job_s3_tag.run(activation_table, ses)

    except Exception as err:
        print(f'Error: daily job task failed {err}')
        ses.send_email_task_failed(
            'Error: daily job task failed',
            f'Error: daily job task failed. Options: {str(options)}',
            err,
            options["email_from_addr"],
            options["email_to_addr"])


def parse_args(args) -> ArgumentParser:
    """Parses the parameters when main.py is called

    Returns
    -------
    ArgumentParser
        An object containing all the parameter values or their defaults
    """
    description = ('Run centralized daily jobs in one region (us-east-1)')
    parser = ArgumentParser(description=description)
    parser.add_argument('--aws_account_id', type=str, required=True,
                        help='The aws account id that will run jobs')
    parser.add_argument('--dynamodb_region', type=str, required=True,
                        help='The region of the dynamodb tables')
    parser.add_argument('--dynamodb_activation_table', type=str, required=True,
                        help='The name of the dynamodb activation table')
    parser.add_argument('--lambda_region', type=str, required=True,
                        help='The region when lambdas are deployed')
    parser.add_argument('--s3_tag_lambda_name', type=str, required=True,
                        help='S3 tagging lambda name')
    parser.add_argument('--s3_tag_lambda_role_arn', type=str, required=True,
                        help='S3 tagging lambda execution role name')
    parser.add_argument('--s3_manifest_bucket', type=str, required=True,
                        help='S3 tagging lambda manifest bucket')
    parser.add_argument('--environment', type=str, required=True,
                        help='Environment name')
    parser.add_argument('--email_from_addr', type=str, required=False,
                        help='The FROM email address for email notifications')
    parser.add_argument('--email_to_addr', type=str, required=False,
                        help='The TO email address for email notifications')
    return parser.parse_args(args)


if __name__ == '__main__':
    # Usage: python3 main.py <args>
    # See unit and integration tests for working examples
    config = parse_args(sys.argv[1:])
    print(f'Running daily job tasks, with args: {str(config)}')
    main(vars(config))
    print('Done')

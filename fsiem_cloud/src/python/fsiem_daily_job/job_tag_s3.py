import json
import boto3
from datetime import datetime
from fsiem_api_client import ActivationTable
from fsiem_api_client.aws.ses import Ses


class JobTagS3:

    def __init__(self,
                 aws_account_id: str,
                 lambda_region: str,
                 s3_tag_lambda_name: str,
                 s3_tag_lambda_role_arn: str,
                 s3_manifest_bucket: str,
                 environment: str,
                 email_from_addr: str,
                 email_to_addr: str
                 ) -> None:
        """S3 tagging job"""
        self.aws_account_id = aws_account_id
        self.lambda_region = lambda_region
        self.lambda_name = s3_tag_lambda_name
        self.lambda_role_arn = s3_tag_lambda_role_arn
        self.s3_manifest_bucket = s3_manifest_bucket
        self.environment = environment
        self.email_from_addr = email_from_addr
        self.email_to_addr = email_to_addr

        # This context helps identifying who calls the lambda
        aws_account = boto3.client('sts').get_caller_identity()
        self.client_context = {
            'caller': 'S3TagJob',
            'invoked_on': None,
            'aws_user_id': aws_account['UserId'],
            'aws_account': aws_account['Account'],
            'aws_arn': aws_account['Arn'],
        }

        self.client = boto3.client('lambda', region_name=lambda_region)

    def _get_payload(self, region: str, sn: str, data_type: str) -> dict:
        """Make JSON payload for the S3 tag lambda object"""
        bucket = f'fsiem-clickhouse-{data_type}-{region}-{self.environment}'
        payload = {
            'region': region,
            'sn': sn,
            'account_id': self.aws_account_id,
            'role_arn': self.lambda_role_arn,
            'manifest_bucket': self.s3_manifest_bucket,
            'manifest_tags': f'SerialNumber={sn}',
            'bucket': bucket,
            'prefix': sn
        }
        return payload

    def _invoke_async_s3_tag_lambda(self, payload: dict, ses: Ses) -> dict:
        """Async call AWS Lambda. Returns once the call was enqueued,
        but doesn't wait until Lambda is finished.

        This is fire-and-forget call. There may only be errors if the call
        fails to enqueue lambda for execution, e.g. lambda name is wrong,
        lack of permissions, or wrong region.

        If this fails, we will attempt to send an email to dev team
        """
        payload_str = json.dumps(payload)
        # Async call to lambda
        return self.client.invoke(
            FunctionName=self.lambda_name,
            InvocationType='Event',
            ClientContext=json.dumps(self.client_context),
            Payload=payload_str)

    def _run_task(self, deployment: dict, ses: Ses):
        """Tag data and backup S3 folders for a single deployment"""
        try:
            sn = deployment['serialNumber']['S']
            region = deployment['region']['S']

            payload = self._get_payload(region, sn, 'data')
            self.client_context['invoked_on'] = datetime.utcnow().isoformat()
            print(f'Running S3 tag job for {sn} in {region}: {payload}')
            resp = self._invoke_async_s3_tag_lambda(payload, ses)
            print(f'Lambda response: {resp}')

            payload = self._get_payload(region, sn, 'backups')
            self.client_context['invoked_on'] = datetime.utcnow().isoformat()
            print(f'Running S3 tag job for {sn} in {region}: {payload}')
            resp = self._invoke_async_s3_tag_lambda(payload, ses)
            print(f'Lambda response: {resp}')
        except Exception as err:
            print(f'Error: S3 tagging for clickhouse failed {err}')
            ses.send_email_task_failed(
                f'S3 tagging for clickhouse {payload["sn"]}',
                f'S3 tagging for clickhouse data. Options: {str(payload)}',
                err,
                self.email_from_addr,
                self.email_to_addr)

    def run(self, activation_table: ActivationTable, ses: Ses):
        """Tag data and backup S3 folders for all deployments"""
        print('Running S3 tag jobs')
        deployments = activation_table.get_all_items()
        for deployment in deployments:
            self._run_task(deployment, ses)

from fsiem_api_client.aws.ses import Email, Ses
from botocore.exceptions import WaiterError


class TestSes:

    uut = Ses(region='us-east-1')
    example_failure = {
        "CommandId": "f66d7e39-15d7-443e-9011-1cd0addb2e49",
        "InstanceId": "i-0833da245549e057a",
        "Comment": "",
        "DocumentName": "AWS-RunShellScript",
        "DocumentVersion": "$DEFAULT",
        "PluginName": "aws:runShellScript",
        "ResponseCode": 137,
        "ExecutionStartDateTime": "2023-05-07T22:13:33.797Z",
        "ExecutionElapsedTime": "PT1H0.271S",
        "ExecutionEndDateTime": "2023-05-07T23:13:33.797Z",
        "Status": "TimedOut",
        "StatusDetails": "ExecutionTimedOut",
        "StandardOutputContent": "",
        "StandardOutputUrl": "",
        "StandardErrorContent": "",
        "StandardErrorUrl": "",
        "CloudWatchOutputConfig": {
            "CloudWatchLogGroupName": "",
            "CloudWatchOutputEnabled": False
        },
        "ResponseMetadata": {
            "RequestId": "dde4f556-8ecb-4088-b0b6-f331947d591a",
            "HTTPStatusCode": 200,
            "HTTPHeaders": {
                "server": "Server",
                "date": "Sun, 07 May 2023 23:13:38 GMT",
                "content-type": "application/x-amz-json-1.1",
                "content-length": "597",
                "connection": "keep-alive",
                "x-amzn-requestid": "dde4f556-8ecb-4088-b0b6-f331947d591a"
            },
            "RetryAttempts": 0
        }
    }

    backup_options = {
        'remote_storage': 's3',
        'log_level': 'WARN',
        's3_compression_level': '1',
        's3_compression_format': 'tar',
        's3_use_custom_storage_class': 'false',
        's3_storage_class': 'STANDARD',
        's3_concurrency': '1',
        's3_debug': 'false',
        'max_backups_in_chain': '3'
    }

    from_address = "no-reply@mail.playground.fortisiem.cloud"
    to_addresses = 'omandrychenko@fortinet.com'

    def test_send_email(self):
        email = Email(
            from_address=self.from_address,
            to_addresses=[self.to_addresses],
            subject='fsiem_api_client:email integration test',
            body_text='integration test - please ignore')
        resp = self.uut.send_email(email)
        assert resp

    def test_send_email_failure(self):
        err = WaiterError('name', 'description', self.example_failure)
        desc = f'''
            SSM task to execute clickhouse-backup.
            Options: {str(self.backup_options)}
            Backup name: 2023-05-23-01-full
            Backup type: full
            Previous backup: {None}
            '''
        resp = self.uut.send_email_task_failed(
            'run_backup', desc, err, self.from_address, self.to_addresses)
        assert resp

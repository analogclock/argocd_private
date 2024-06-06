from dataclasses import dataclass, field
import boto3

from fsiem_api_client.exceptions import ExceptionInfo


@dataclass
class Email:
    from_address: str
    to_addresses: list[str] = field(default_factory=list)
    cc_addresses: list[str] = field(default_factory=list)
    bcc_addresses: list[str] = field(default_factory=list)
    reply_to_addresses: list[str] = field(default_factory=list)
    charset: str = 'utf-8'
    subject: str = ''
    body_text: str = None


class Ses:
    """A client class for AWS SES (Simple Email Service)"""

    def __init__(self, region: str = 'us-east-1') -> None:
        # This requires manual configuration which was done in us-east-1
        # If you need to send an email from a different region, just use
        # us-east-1 for quick access to AWS SES functionality.
        self.client = boto3.client('ses', region_name=region)

    def send_email_task_failed(
            self,  task_name: str, task_desc: str, err: Exception,
            from_addr: str, to_addr: str,
            reply_to_addr: str = 'no-reply@fortinet.com') -> dict | None:
        """Send an email with details about why a task failed"""

        email = self._create_task_failed_email(
            task_name,
            task_desc,
            err,
            from_addr,
            to_addr,
            reply_to_addr)

        return self.send_email(email)

    def send_email(self, email: Email) -> dict | None:
        """Sends an email though AWS Simple Email Service

        Parameters
        ----------
        email : Email
            An email object to send
        """

        print(f'Sending email to {email.to_addresses}')
        print(f'Subject: {email.subject}')
        try:
            return self.client.send_email(
                Source=email.from_address,
                Destination={
                    'ToAddresses': email.to_addresses,
                    'CcAddresses': email.cc_addresses,
                    'BccAddresses': email.bcc_addresses,
                },
                Message={
                    'Subject': {
                        'Data': email.subject,
                        'Charset': email.charset
                    },
                    'Body': {
                        'Text': {
                            'Data': email.body_text,
                            'Charset': email.charset
                        }
                    }
                },
                ReplyToAddresses=email.reply_to_addresses
            )
        except Exception as err:
            print(f'Failed to send an email, error: {err}')
            return None

    def send_email_html(self, email: Email) -> dict | None:
        """Sends an email though AWS Simple Email Service with an HTML body

        Parameters
        ----------
        email : Email
            An email object to send
        """

        print(f'Sending email to {email.to_addresses}')
        print(f'Subject: {email.subject}')
        try:
            return self.client.send_email(
                Source=email.from_address,
                Destination={
                    'ToAddresses': email.to_addresses,
                    'CcAddresses': email.cc_addresses,
                    'BccAddresses': email.bcc_addresses,
                },
                Message={
                    'Subject': {
                        'Data': email.subject,
                        'Charset': email.charset
                    },
                    'Body': {
                        'Html': {
                            'Data': email.body_text,
                            'Charset': email.charset
                        }
                    }
                },
                ReplyToAddresses=email.reply_to_addresses
            )
        except Exception as err:
            print(f'Failed to send an email, error: {err}')
            return None

    def _create_task_failed_email(
            self, task_name: str, task_desc: str, err: Exception,
            from_addr: str, to_addr: str,
            reply_to_addr: str = 'no-reply@fortinet.com') -> Email:
        """Create an Email object from task details, including formatted error
           details."""

        subject = f'Task failed: {task_name}'
        exception_msg = ExceptionInfo.format(err)
        body = f'''
        Task failed: {task_name}

        Task description: {task_desc}

        Error:
        {exception_msg}
        '''
        return Email(from_address=from_addr, to_addresses=[to_addr],
                     reply_to_addresses=[reply_to_addr], subject=subject,
                     body_text=body)

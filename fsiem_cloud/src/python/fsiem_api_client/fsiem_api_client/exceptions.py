import traceback
import json
from botocore.exceptions import WaiterError
from requests.exceptions import HTTPError


class UnauthorizedHttpError(HTTPError):
    """Received a 401 HTTP response from target."""


class ExceptionInfo:

    @staticmethod
    def format(e: Exception) -> str:
        """Create a string representation of exception.

        If exception is a WaiterError (used for SSM calls), then details about
        the last call will be added.

        Traceback module is used to format the exception into a message

        Parameters
        ----------
        e : Exception
            Exception details

        Returns
        -------
        str
            A multi-line string with text representation of the error. It may
            include json document for WaiterError and it will include exception
            message and a call stack
        """
        msg = ''
        if isinstance(e, WaiterError):
            msg += json.dumps(e.last_response, indent=2)
            msg += '\n'

        msg += '\n'.join(traceback.format_exception(e))
        return msg

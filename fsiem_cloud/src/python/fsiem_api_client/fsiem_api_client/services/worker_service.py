from enum import Enum
from json import loads
from fsiem_api_client.http_call import HttpCall


class WORKER_TYPE(Enum):
    EVENT = 'event'
    QUERY = 'query'


class WORKER_ACTION(Enum):
    GET = 'get'
    ADD = 'add'
    DEL = 'delete'


class WorkerService:

    def __init__(self, http: HttpCall, super_url: str):
        if not http:
            raise ValueError('http cannot be None.')
        if not super_url:
            raise ValueError('super url cannot be None.')
        self.http = http
        self.super_url = super_url

    # noqa - means No QA, this will allow longer lines for linter
    _urls = [
        (WORKER_ACTION.GET, WORKER_TYPE.EVENT, '/phoenix/rest/system/eventworker'),         # noqa
        (WORKER_ACTION.ADD, WORKER_TYPE.EVENT, '/phoenix/rest/system/add/eventworker'),     # noqa
        (WORKER_ACTION.DEL, WORKER_TYPE.EVENT, '/phoenix/rest/system/delete/eventworker'),  # noqa
        (WORKER_ACTION.GET, WORKER_TYPE.QUERY, '/phoenix/rest/system/queryworker'),         # noqa
        (WORKER_ACTION.ADD, WORKER_TYPE.QUERY, '/phoenix/rest/system/add/queryworker'),     # noqa
        (WORKER_ACTION.DEL, WORKER_TYPE.QUERY, '/phoenix/rest/system/delete/queryworker')   # noqa
        ]

    def _url_from(self, action: WORKER_ACTION, type: WORKER_TYPE) -> str:
        """Given an action and worker type, return a URL that matches this
           action and type. E.g.
           >>> url = _url_from(WORKER_ACTION.GET, WORKER_TYPE.EVENT)
           >>> print(url)
           >>> 'https://example.com/phoenix/rest/system/eventworker'
           """
        for (a, t, u) in self._urls:
            if a == action and t == type:
                return f'{self.super_url}{u}'
        raise ValueError(f'URL for \'{action}\' and \'{type}\' not found')

    def get(self, type: WORKER_TYPE) -> list:
        """Get the existing event or query worker addresses

        Parameters
        ----------
        type : WORKER_TYPE
            The worker type to get, event or query

        Returns
        -------
        list
            A list of the current event worker addresses
        """
        url = self._url_from(WORKER_ACTION.GET, type)
        r = self.http.get(url)

        # Response just contains this text if there are no workers
        if r.text == 'No event worker exists':
            return []
        else:
            json = loads(r.text)
            return json['addresses']

    def add(self, worker_url: str, type: WORKER_TYPE):
        """Add URL to the event or query worker

        Parameters
        ----------
        worker_url : str
            Worker URL to add
        type : WORKER_TYPE
            The worker type to get, event or query
        """
        url = self._url_from(WORKER_ACTION.ADD, type)
        r = self.http.post(url, json={'addresses': [worker_url]})
        json = loads(r.text)
        self.http.verify_resp_for_item(json, worker_url)

    def delete(self, workers: list, type: WORKER_TYPE):
        """Delete URLs from the event or query worker

        Parameters
        ----------
        event_workers : list
            A list of worker URLs to delete
        type : WORKER_TYPE
            Worker type: event or query
        """
        url = self._url_from(WORKER_ACTION.DEL, type)
        r = self.http.post(url, json={'addresses': workers})
        json = loads(r.text)
        self.http.verify_resp_for_list(json, workers)

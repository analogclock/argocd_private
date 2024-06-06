from json import loads
from fsiem_api_client.http_call import HttpCall


class HealthService:

    path_metrics = '/phoenix/rest/system/health'
    path_metrics_summary = '/phoenix/rest/system/health/summary'

    def __init__(self, http: HttpCall, super_url: str):
        if not http:
            raise ValueError('http cannot be None.')
        if not super_url:
            raise ValueError('super url cannot be None.')
        self.http = http
        self.super_url = super_url

    def get_metrics(self) -> dict:
        """Retrieve the fsiem cluster metrics from the health API

        Returns
        -------
        dict
            Json object of all the metrics returned by the API
        """
        url = f'{self.super_url}{self.path_metrics}'
        r = self.http.get(url, verbose=False)
        return loads(r.text)

    def get_health_summary(self) -> list:
        """Retrieve the fsiem cluster health summary from the health API

        Returns
        -------
        list
            Json object of the metrics summary
        """
        url = f'{self.super_url}{self.path_metrics_summary}'
        r = self.http.get(url, verbose=False)
        return loads(r.text)

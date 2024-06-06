import agent_util
from os import environ
from enum import IntEnum
from json import load
from fsiem_api_client.util import get_client
from fsiem_api_client.fsiem_api import FsiemApi


nodes_path = '/tmp/nodes.json'
fsm_summary_path = '/tmp/fms_summary.json'
fsm_metrics_path = '/tmp/fsm_metrics.json'
clickhouse_metrics_path = '/tmp/clickhouse_metrics.json'
clickhouse_duration_path = '/tmp/clickhouse_duration.json'
clickhouse_query_count_path = '/tmp/clickhouse_count.json'

with open('/tmp/vars.json', 'r') as var_file:
    data = load(var_file)
    super_url = data['super_url']
    client_id = data['client_id']
    client_secret = data['client_secret']
    cognito_url = data['cognito_url']
    serial_number = data['serial_number']
    region = data['region']
    environ['AWS_CONTAINER_CREDENTIALS_RELATIVE_URI'] = data['aws_creds_url']


class SUMMARY_TYPE(IntEnum):
    NORMAL = 3
    WARNING = 2
    CRITICAL = 1
    UNKNOWN = 0


def get_fsiem() -> FsiemApi:
    secret_auth = {'client_id': client_id, 'client_secret': client_secret}
    return get_client(super_url, secret_auth, cognito_url, max_retry=10,
                      verify_tls=False)


def get_nodes() -> dict:
    try:
        with open(nodes_path, 'r') as node_file:
            nodes = load(node_file)
    except Exception:
        # Make this better
        nodes = {
            'all': [],
            'supers': [],
            'workers': [],
            'keepers': [],
            'collectors': []
        }
    return nodes


# Template taken from:
# https://confluence-panopta.atlassian.net/wiki/spaces/PD/pages/718831637/template.py+file
class FsiemPlugin(agent_util.Plugin):
    textkey = "fsiem"
    label = "FortiSiem"

    @classmethod
    def get_metadata(self, config):
        msg = None
        instance_list = get_nodes()
        self.log.info(f'Supers found: {instance_list["supers"]}')
        self.log.info(f'Workers found: {instance_list["workers"]}')
        self.log.info(f'Ingestion workers found: {instance_list["ingestion"]}')
        self.log.info(f'Keepers found: {instance_list["keepers"]}')
        self.log.info(f'Collectors found: {instance_list["collectors"]}')

        status = agent_util.SUPPORTED
        metadata = {
            "status_summary": {
                "label": "Status Summary",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "status_node": {
                "label": "Node Status Summary",
                "options": instance_list['all'],
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "collector_status": {
                "label": "Collector Status Summary",
                "options": instance_list['collectors'],
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "eps3m": {
                "label": "Events/Second 3 min",
                "options": instance_list['all'],
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "collector_eps3m": {
                "label": "Collector Events/Second 3 min",
                "options": instance_list['collectors'],
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "eventQueue": {
                "label": "Events Queue",
                "options": instance_list['all'],
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "clickhouse_queries_executing": {
                "label": "Clickhouse Executing Queries",
                "options": instance_list['workers'],
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "clickhouse_merges_executing": {
                "label": "Clickhouse Executing Merges",
                "options": instance_list['workers'],
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "clickhouse_query_duration": {
                "label": "Clickhouse Query Duration Milliseconds",
                "options": instance_list['workers'],
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "clickhouse_query_select_clickhouse": {
                "label": "Clickhouse Query Select Clickhouse",
                "options": instance_list['workers'],
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "clickhouse_query_select_clickhouse_client": {
                "label": "Clickhouse Query Select Clickhouse Client",
                "options": instance_list['workers'],
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "clickhouse_query_select_unknown": {
                "label": "Clickhouse Query Select Clickhouse Unknown or HTTP",
                "options": instance_list['workers'],
                "status": status,
                "error_message": msg,
                "unit": "count"
            }
        }
        return metadata

    def check(self, textkey: str, instance: str, config: dict):
        self.log.info(f'textkey: {textkey}')
        self.log.info(f'Instance: {instance}')
        summary_metrics = self.get_metrics_from_file(fsm_summary_path)
        api_metrics = self.get_metrics_from_file(fsm_metrics_path)
        ch_metrics = self.get_metrics_from_file(
            clickhouse_metrics_path)
        ch_duration_metrics = self.get_metrics_from_file(
            clickhouse_duration_path)
        ch_count_metrics = self.get_metrics_from_file(
            clickhouse_query_count_path)
        match textkey:
            case 'clickhouse_queries_executing':
                return float(ch_metrics[instance]['Query'])
            case 'clickhouse_merges_executing':
                return float(ch_metrics[instance]['Merge'])
            case 'clickhouse_query_duration':
                return float(ch_duration_metrics[instance]['avg_duration'])
            case 'clickhouse_query_select_clickhouse':
                return float(
                    ch_count_metrics[instance]['Select']['ClickHouse'])
            case 'clickhouse_query_select_clickhouse_client':
                return float(
                    ch_count_metrics[instance]['Select']['ClickHouse client']
                )
            case 'clickhouse_query_select_unknown':
                return float(
                    ch_count_metrics[instance]['Select']['unknown_or_http']
                )
            case 'status_summary':
                self.log.info(f'Summary {summary_metrics}')
                return self.get_summary(api_metrics)
            case 'status_node' | 'collector_status':
                return self.get_node_summary(api_metrics, instance)
            case 'eps3m' | 'collector_eps3m':
                return self.get_eps(api_metrics, instance, '3min')
            case 'eventQueue':
                return self.get_event_queue(api_metrics, instance)
        return 0

    def get_metrics_from_file(self, path: str) -> dict:
        try:
            with open(path, 'r') as metrics_file:
                metrics = load(metrics_file)
        except Exception:
            self.log.error(f'Failed to load {path}')
            metrics = {}
        return metrics

    def get_summary(self, api_metrics: dict) -> int:
        status = api_metrics['healthStatus']
        return self.get_status(status)

    def get_node_summary(self, api_metrics: dict, instance: str) -> int:
        # Default value in case we cant find it in the metrics
        status = 'Unknown'
        for node in api_metrics['nodes']:
            if node['summary']['name'] == instance:
                status = node['summary']['status']
                break
        return self.get_status(status)

    def get_status(self, status: str) -> SUMMARY_TYPE:
        if status == 'Normal':
            return SUMMARY_TYPE.NORMAL
        elif status == 'Warning':
            return SUMMARY_TYPE.WARNING
        elif status == 'Critical':
            return SUMMARY_TYPE.CRITICAL
        else:
            return SUMMARY_TYPE.UNKNOWN

    def get_eps(self, api_metrics: dict, instance: str,
                time_range: str) -> float:
        for node in api_metrics['nodes']:
            if node['summary']['name'] == instance:
                return node['metrics']['eps'][time_range]

    def get_event_queue(self, api_metrics: dict, instance: str) -> float:
        for node in api_metrics['nodes']:
            if node['summary']['name'] == instance:
                return node['metrics']['eventUploadQueue']['queue']

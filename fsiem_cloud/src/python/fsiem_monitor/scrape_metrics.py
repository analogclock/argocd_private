from json import loads, load, dump
from os import environ
from datetime import datetime
from fsiem_api_client.util import get_client
from fsiem_api_client.fsiem_api import FsiemApi
from fsiem_api_client.aws.ssm_ops import SsmOps
from fsiem_api_client.aws.ec2 import Ec2


nodes_path = '/tmp/nodes.json'
fsm_summary_path = '/tmp/fms_summary.json'
fsm_metrics_path = '/tmp/fsm_metrics.json'
clickhouse_metrics_path = '/tmp/clickhouse_metrics.json'
clickhouse_duration_path = '/tmp/clickhouse_duration.json'
clickhouse_query_count_path = '/tmp/clickhouse_count.json'
datetime_format = '%Y-%m-%d %H:%M:%S'


def get_fsiem() -> FsiemApi:
    secret_auth = {'client_id': client_id, 'client_secret': client_secret}
    return get_client(super_url, secret_auth, cognito_url, max_retry=10,
                      verify_tls=False)


def get_fsiem_summary(fsiem: FsiemApi) -> list:
    try:
        summary = fsiem.health.get_health_summary()
    except Exception:
        summary = []

    print(summary, flush=True)
    with open(fsm_summary_path, 'w') as json_file:
        dump(summary, json_file)

    return summary


def get_nodes(summary: list) -> dict:
    ec2 = Ec2(region=region)

    supers = []
    workers = []
    ingestion = []
    keepers = []
    collectors = []
    for node in summary[0]['nodes']:
        dns_name = node['name']
        node_type = node['nodeType']
        if node_type == 'Super':
            supers.append(dns_name)
        elif node_type == 'Collector':
            collectors.append(dns_name)
        elif node_type == 'Worker':
            instances = ec2.get_instance_info_from_dns(
                serial_number, dns_name)
            if len(instances) < 1:
                continue
            tags = instances[0]['Tags']
            role = next(
                (tag for tag in tags if tag['Key'] == 'Role'), None)['Value']
            if role == 'worker':
                workers.append(dns_name)
            elif role == 'keeper':
                keepers.append(dns_name)
            elif role == 'ingestion':
                ingestion.append(dns_name)

    nodes = {
        'all': supers + workers + keepers + ingestion,
        'supers': supers,
        'workers': workers,
        'ingestion': ingestion,
        'keepers': keepers,
        'collectors': collectors
    }
    print(nodes, flush=True)
    # Output to json file in /tmp
    with open(nodes_path, 'w') as json_file:
        dump(nodes, json_file)
    return nodes


def get_fsiem_metrics(fsiem: FsiemApi) -> dict:
    """Get the fortisiem metrics from the health API

    Returns
    -------
    dict
        {
            "id": 1,
            "name": "Super",
            "healthStatus": "Normal",
            "nodes": [
                ...
            ]
        }
    """
    # raise HTTPError(http_error_msg, response=self)
    metrics = fsiem.health.get_metrics()

    # Flattens the response as we don't care about the different orgs the
    # customer might have made, so we put all the nodes under the default
    # org with id 1
    metric_map = {}
    nodes = []
    for org in metrics['instances']:
        if org['id'] == 1:
            metric_map = org
        nodes.extend(org['nodes'])
    metric_map['nodes'] = nodes
    print(metric_map, flush=True)
    with open(fsm_metrics_path, 'w') as json_file:
        dump(metric_map, json_file)


def get_clickhouse_metrics(nodes: list):
    ssm = SsmOps(region=region, sn=serial_number)
    clickhouse_metrics = {}
    for instance_dns in nodes:
        response = ssm.clickhouse_metrics(instance_dns)
        output = loads(response.output)
        metrics = sort_clickhouse_metrics_response(output)
        clickhouse_metrics[instance_dns] = metrics
    print(clickhouse_metrics, flush=True)
    with open(clickhouse_metrics_path, 'w') as json_file:
        dump(clickhouse_metrics, json_file)


def sort_clickhouse_metrics_response(output: dict) -> dict:
    metrics = {}
    for metric in output['data']:
        metrics[metric['metric']] = metric['value']
    return metrics


def get_clickhouse_query_duration(nodes: list):
    ssm = SsmOps(region=region, sn=serial_number)
    clickhouse_metrics = {}
    for instance_dns in nodes:
        response = ssm.clickhouse_query_duration(instance_dns)
        output = loads(response.output)
        metrics = sort_query_duration_response(output)

        clickhouse_metrics[instance_dns] = metrics
    print(clickhouse_metrics, flush=True)
    with open(clickhouse_duration_path, 'w') as json_file:
        dump(clickhouse_metrics, json_file)


def sort_query_duration_response(output: dict) -> dict:
    date_sets = {}
    for data_set in output['data']:
        # Find latest time
        date_object = datetime.strptime(
            data_set['event_time_h'], datetime_format
        )
        date_sets[date_object] = data_set

    # Find latest time from results and return only that
    latest_time = max(dt for dt in date_sets.keys())
    return date_sets[latest_time]


def get_clickhouse_query_counts(nodes: list):
    ssm = SsmOps(region=region, sn=serial_number)
    clickhouse_metrics = {}
    for instance_dns in nodes:
        response = ssm.clickhouse_query_count(instance_dns)
        output = loads(response.output)
        metrics = sort_query_count_response(output)
        clickhouse_metrics[instance_dns] = metrics
    print(clickhouse_metrics, flush=True)
    with open(clickhouse_query_count_path, 'w') as json_file:
        dump(clickhouse_metrics, json_file)


def sort_query_count_response(output: dict) -> dict:
    # Get latest timestamp
    date_list = []
    for data_set in output['data']:
        date_object = datetime.strptime(
            data_set['event_time_m'], datetime_format
        )
        date_list.append(date_object)

    # Find latest time from results
    latest_time = max(date_list)

    # Order results into dict
    select = 'Select'
    results = {
        select: {}
    }
    for data_set in output['data']:
        if data_set['event_time_m'] == latest_time.strftime(datetime_format):
            client = data_set['client_name']
            kind = data_set['query_kind']
            count = data_set['count()']
            if kind == select:
                results[select][client] = count
            else:
                print('We currently only collect metrics for Select queries',
                      flush=True)
    print(results)
    return results


if __name__ == '__main__':
    with open('/tmp/vars.json', 'r') as var_file:
        data = load(var_file)
        super_url = data['super_url']
        client_id = data['client_id']
        client_secret = data['client_secret']
        cognito_url = data['cognito_url']
        serial_number = data['serial_number']
        region = data['region']
        uri = 'AWS_CONTAINER_CREDENTIALS_RELATIVE_URI'
        environ[uri] = data['aws_creds_url']

    fsiem = get_fsiem()
    print('Getting fsiem summary', flush=True)
    summary = get_fsiem_summary(fsiem)
    print('Retrieving nodes', flush=True)
    nodes = get_nodes(summary)
    print('Getting fsiem metrics', flush=True)
    get_fsiem_metrics(fsiem)
    print('Getting clickhouse metrics', flush=True)
    get_clickhouse_metrics(nodes['workers'])
    print('Getting clickhouse query duration', flush=True)
    get_clickhouse_query_duration(nodes['workers'])
    print('Getting clickhouse query counts', flush=True)
    get_clickhouse_query_counts(nodes['workers'])
    print('Finished', flush=True)

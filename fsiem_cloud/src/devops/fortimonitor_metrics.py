import requests
from urllib.parse import urlparse


# Change this to a valid FortiMonitor API token
token = ''

headers = {
    'Content-type': 'application/json',
    'Authorization': f'ApiKey {token}'
}


def get_id(url: str) -> str:
    """FortiMonitors API doesn't just give you the id of the resource, instead
    we need to find it ourselves by breaking down the URLs they give us. Fun.

    Parameters
    ----------
    url : str
        The url it returns

    Returns
    -------
    str
        The ID
    """
    url_object = urlparse(url)
    return int(url_object.path.split('/')[-1])


def get_server_id(api_url: str, serial_no: str) -> int:
    server_url = f'{api_url}/server'
    params = {
        'limit': 50,
        'offset': 0,
        'attribute_filter_mode': 'or',
        'tag_filter_mode': 'and',
        'tags': f'{serial_no},super'
    }
    response = requests.get(server_url,
                            params=params,
                            headers=headers,
                            verify=True)

    resp_json = response.json()

    # Should only be 1 instance return for super, add a check
    # print(len(resp_json['server_list']))

    # Have to get server_id from url as its not supplied elsewhere
    url_object = urlparse(resp_json['server_list'][0]['url'])
    return int(url_object.path.split('/')[-1])


def get_metric_id(api_url: str, server_id: int, metric_name: str) -> int:
    resource_url = f'{api_url}/server/{server_id}/agent_resource'

    params = {
        'limit': 100,
        'full': True,
        'name': metric_name
    }

    response = requests.get(
        resource_url,
        params=params,
        headers=headers,
        verify=True
    )
    resp_json = response.json()

    for resource in resp_json['agent_resource_list']:
        metric_id = get_id(resource['url'])
    return metric_id


def get_metrics(api_url: str, server_id: int, metric_id: int):
    metric_url = (
        f'{api_url}/server/{server_id}/agent_resource/{metric_id}/metric/hour'
    )
    response = requests.get(
        metric_url,
        headers=headers,
        verify=True
    )
    print(response.text)


if __name__ == '__main__':
    api_url = 'https://api2.panopta.com/v2'
    serial_no = 'FSMCLD0000000165'

    server_id = get_server_id(api_url, serial_no)

    # EPS
    eps_id = get_metric_id(api_url, server_id, 'Events/Second average 3 min')
    get_metrics(api_url, server_id, eps_id)

    # CPU
    cpu_id = get_metric_id(api_url, server_id, 'CPU % Used')
    get_metrics(api_url, server_id, cpu_id)

    # Memory
    memory_id = get_metric_id(api_url, server_id, 'Memory: RAM % usage')
    get_metrics(api_url, server_id, memory_id)

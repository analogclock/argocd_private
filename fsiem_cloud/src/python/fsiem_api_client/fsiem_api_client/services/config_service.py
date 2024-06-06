from string import Template
from requests import Response
from fsiem_api_client.http_call import HttpCall


class ConfigService:

    deploy_type_url = '/phoenix/rest/system/systemConfigs'
    deploy_type_template = Template("""
        <config>
          <systemConfigs>
            <systemConfig>
              <category>Message</category>
              <name>deployment_type</name>
              <value>$value</value>
            </systemConfig>
          </systemConfigs>
        </config>
        """)

    def __init__(self, http: HttpCall, super_url: str):
        if not http:
            raise ValueError('http cannot be None.')
        if not super_url:
            raise ValueError('super url cannot be None.')
        self.http = http
        self.super_url = super_url

    def set_deployment_type_cloud(self) -> Response:
        return self._set_deployment_type('cloud')

    def set_deployment_type_local(self) -> Response:
        return self._set_deployment_type('local')

    def _set_deployment_type(self, deployment_type: str) -> Response:
        if deployment_type not in ['local', 'cloud']:
            raise ValueError(f'Unexpected deployment type: {deployment_type}')
        data = self.deploy_type_template.substitute(value=deployment_type)
        headers = {'Content-type': 'application/xml'}
        url = f'{self.super_url}{self.deploy_type_url}'
        return self.http.put(url, data=data, headers=headers)

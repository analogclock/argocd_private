
import boto3
import requests
import xml.etree.ElementTree as ET

from requests import Response


def make_xml_payload(event: dict) -> str:
    password = event['Password']
    org_user = event['OrgUser']
    org_name = event['OrgName']
    collector_eps = event['CollectorEps']
    collector_name = event['CollectorName']

    xml = f"""<organizations>
                <organization>
                    <name>{org_name}</name>
                    <fullName>Test organization 400</fullName>
                    <description>organization 400 account</description>
                    <adminUser>{org_user}</adminUser>
                    <adminPwd>{password}</adminPwd>
                    <adminEmail>test@test.com</adminEmail>
                    <custResource>
                        <diskQuote>536870912000</diskQuote>
                        <eps>100000</eps>
                        <configItem>300</configItem>
                        <duration>365</duration>
                    </custResource>
                    <collectors>
                    </collectors>
                </organization>
                </organizations>"""

    # Split the collector names received as string
    collectors = [x.strip() for x in collector_name.split(',')]
    print(f'Collectors that have to be added are: {collectors}')

    # Append the xml to add all collectors
    updated_xml = xml
    # Parse the XML string into an Element object
    root = ET.fromstring(updated_xml)
    for collector in collectors:
        print(f'Collector : {collector}')
        # Get the third level subelement
        collector_level = root.find('./organization/collectors')
        # Create a new element (collector) with three child elements
        # 'eps','collector name' & 'registered'
        # append it to the third level subelement
        el = ET.Element('collector')
        child_el1 = ET.Element('eps')
        child_el1.text = collector_eps
        child_el2 = ET.Element('name')
        child_el2.text = collector
        child_el3 = ET.Element('registered')
        child_el3.text = 'false'
        el.append(child_el1)
        el.append(child_el2)
        el.append(child_el3)
        collector_level.append(el)
    # Convert the Element object back to an XML string
    return ET.tostring(root, encoding='unicode')


def add_org_collectors_to_super(event: dict) -> Response:
    user = event['User']
    super_user = f'super/{user}'
    password = event['Password']
    super = event['SuperUrl']
    uri = f'{super}/phoenix/rest/organization/add'

    headers = {'Content-type': 'application/xml'}
    data = make_xml_payload(event)
    print(f'HTTP PUT {uri}:\n {data}')
    r = requests.put(uri, auth=(super_user, password),
                     data=data, headers=headers)
    print("Status code: ", r.status_code)
    print("Reason: ", r.reason)
    r.raise_for_status()
    return r


def provision_collectors(event: dict):
    serial_number = event['SerialNumber']
    environment = event['EnvId']
    password = event['Password']
    org_user = event['OrgUser']
    super = event['SuperUrl']
    org_name = event['OrgName']
    collector_name = event['CollectorName']

    # Split the collector names received as string
    collectors = [x.strip() for x in collector_name.split(',')]
    print(f'Collectors that have to be registered are: {collectors}')

    # Get the collectors instance ids
    client = boto3.client('ec2')
    filters = [
        {'Name': 'tag:Environment', 'Values': [f'{environment}']},
        {'Name': 'tag:SerialNumber', 'Values': [f'{serial_number}']},
        {'Name': 'tag:Role', 'Values': ['collector']}
    ]
    response = client.describe_instances(Filters=filters)
    instance_ids = []

    for reservations in response['Reservations']:
        for instance in reservations['Instances']:
            if instance["State"]["Name"] == "running":
                instance_ids.append(instance['InstanceId'])

    # Provisioning the collectors
    ssm = boto3.client('ssm')
    for i, instance_id in enumerate(instance_ids):
        print(f'Collector index: {i}')
        print(f'Instance id iteration: {instance_id}')
        print(f'Provisioning Values: {org_user} {super} {org_name} {collectors[i]}')
        response = ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName="AWS-RunShellScript",
            Parameters={
                'commands': [f'sudo -s /opt/phoenix/bin/phProvisionCollector --add {org_user} {password} {super} {org_name} {collectors[i]}']
            },
            CloudWatchOutputConfig={
                'CloudWatchLogGroupName': '/aws/lambda/lambda_ssm_collectors_auto_playground',
                'CloudWatchOutputEnabled': True
            }
        )
        command_id = response['Command']['CommandId']
        waiter = ssm.get_waiter("command_executed")
        waiter_config = {'Delay': 3, 'MaxAttempts': 20}
        waiter.wait(CommandId=command_id, InstanceId=instance_id,
                    WaiterConfig=waiter_config)
        output = ssm.get_command_invocation(
            CommandId=command_id,
            InstanceId=instance_id
        )
        print(f'Send command output: {output}')

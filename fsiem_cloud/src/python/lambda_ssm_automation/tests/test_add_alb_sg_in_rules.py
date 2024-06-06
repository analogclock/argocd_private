from moto import mock_aws
from add_alb_sg_in_rules import add_alb_sg_in_rules
from tests.aws.aws_helpers import (dynamodb_create_table, dynamodb_put_item,
                                   ec2_create_sg)


@mock_aws
def test_add_alb_sg_in_rules():
    sn = 'FSMCLD0000000152'
    table_name = 'fsiem_activation_table_playground'
    region = 'us-east-1'
    sg_worker = ec2_create_sg('sg_worker', region)
    sg_super = ec2_create_sg('sg_super', region)

    dynamodb_create_table(table_name, region)
    dynamodb_put_item(table_name, region, sn)

    event = {
        'SerialNumber': sn,
        'EnvId': "playground",
        'SecurityGroupIdW': sg_worker,
        'SecurityGroupIdS': sg_super,
        'DynamodbRegion': region,
        'DeploymentRegion': region
    }
    add_alb_sg_in_rules(event)

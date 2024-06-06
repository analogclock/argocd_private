# Program to delete inbound rules to the super & workers ALB's security group
from aws.ec2 import Ec2
from aws.dynamodb import DynamoDb


def delete_alb_sg_in_rules(event):
    """Delete CIDR v4 and v6 networks from the ALB's security group"""
    worker_sg_id = event["SecurityGroupIdW"]
    super_sg_id = event["SecurityGroupIdS"]
    sn = event["SerialNumber"]
    env_id = event["EnvId"]
    dynamodb_region = event['DynamodbRegion']
    region = event['DeploymentRegion']
    table_name = "fsiem_activation_table_" + env_id
    print('Get user-provided Ipv4 and Ipv6 cidr networks from DynamoDb')
    dynamodb = DynamoDb(table_name, region=dynamodb_region)
    cidr_v4 = dynamodb.get_cidr_v4(sn)
    cidr_v6 = dynamodb.get_cidr_v6(sn)

    print('Delete EC2 ALB rules with user-provided cidr networks')
    ec2 = Ec2(region)

    if (cidr_v4):
        print("Deleting ip4 inbound rules for super and worker")
        ec2.revoke_ingress(worker_sg_id, cidr_v4, 'Ipv4')
        ec2.revoke_ingress(super_sg_id, cidr_v4, 'Ipv4')

    if (cidr_v6):
        print("Deleting ip6 inbound rules for super and worker")
        ec2.revoke_ingress(worker_sg_id, cidr_v6, 'Ipv6')
        ec2.revoke_ingress(super_sg_id, cidr_v6, 'Ipv6')

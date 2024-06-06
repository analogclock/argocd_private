import boto3
from moto import mock_aws
from freezegun import freeze_time
from jinja2 import Template, StrictUndefined
from main import (find_near_expiry, prep_emails,
                  remove_blocked_email_addresses)


def create_table(name, region, key_schema):
    client = boto3.client('dynamodb', region_name=region)
    client.create_table(
        TableName=name,
        AttributeDefinitions=[
            {
                'AttributeName': key_schema,
                'AttributeType': 'S'
            }
        ],
        KeySchema=[
            {
                'AttributeName': key_schema,
                'KeyType': 'HASH'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 123,
            'WriteCapacityUnits': 123
        }
    )


def put_item(name, region, item):
    client = boto3.client('dynamodb', region_name=region)
    client.put_item(
        TableName=name,
        Item=item
    )


@freeze_time('2012-02-01')
def test_find_near_expiry():
    deployments = [
        {
            'serialNumber': {
                'S': 'FSMCLD0000000123'
            },
            'deploymentEmail': {
                'S': 'test@test.com'
            },
            'deploymentSKU': {
                'M': {
                    'compute': {
                        'M': {
                            'endDate': {
                                'S': '2012-02-06T00:00:00+00:00'
                            }
                        }
                    }
                }
            }
        },
        {
            'serialNumber': {
                'S': 'FSMCLD0000000124'
            },
            'deploymentEmail': {
                'S': 'test@test.com'
            },
            'deploymentSKU': {
                'M': {
                    'compute': {
                        'M': {
                            'endDate': {
                                'S': '2015-02-01T00:00:00+00:00'
                            }
                        }
                    }
                }
            }
        },
        {
            'serialNumber': {
                'S': 'FSMCLD0000000125'
            },
            'deploymentEmail': {
                'S': 'test@test.com'
            },
            'additionalContacts': {
                'S': 'test1@test.com,test2@test.com'
            },
            'deploymentSKU': {
                'M': {
                    'compute': {
                        'M': {
                            'endDate': {
                                'S': '2012-02-15T00:00:00+00:00'
                            }
                        }
                    }
                }
            }
        }
    ]

    expected = {
        'FSMCLD0000000125': {
            'emails': ['test@test.com', 'test1@test.com', 'test2@test.com'],
            'expiry': 14
        }
    }

    actual = find_near_expiry(deployments)
    assert actual == expected


def test_prep_emails():
    expiries = {
        'FSMCLD0000000123': {
            'emails': ['test@test.com'],
            'expiry': 35
        },
        'FSMCLD0000000124': {
            'emails': ['test@test.com'],
            'expiry': -1
        }
    }

    portal_domain = 'fortisiem.cloud'

    with open('template.html', 'r') as f:
        data = f.read()
    template = Template(data, undefined=StrictUndefined)
    body_123 = template.render(
        current_year=2023,
        serial_no='FSMCLD0000000123',
        expiry_days=35,
        portal_domain=portal_domain,
        type='expiring'
    )

    with open('template.html', 'r') as f:
        data = f.read()
    template = Template(data, undefined=StrictUndefined)
    body_124 = template.render(
        current_year=2023,
        serial_no='FSMCLD0000000124',
        expiry_days=-1,
        portal_domain=portal_domain,
        type='expired'
    )

    expected = [
        {
            'addresses': ['test@test.com'],
            'subject': ('FortiSIEM Cloud: Your deployment FSMCLD0000000123 is '
                        'nearing expiry - 35 days remaining'),
            'body': body_123
        },
        {
            'addresses': ['test@test.com'],
            'subject': ('FortiSIEM Cloud: Your deployment FSMCLD0000000124 has'
                        ' expired'),
            'body': body_124
        }
    ]
    actual = prep_emails(expiries, portal_domain, 2023)
    assert actual == expected


@mock_aws
def test_remove_blocked_email_addresses():
    table_name = 'test_table'
    region = 'us-east-1'
    item = {
        'email': {
            'S': 'test@test.com'
        }
    }
    create_table(table_name, region, 'email')
    put_item(table_name, region, item)

    expiring = {
        'FSMCLD0000000123': {
            'emails': ['test@test.com'],
            'expiry': 35
        },
        'FSMCLD0000000124': {
            'emails': ['test1@test.com', 'test@test.com'],
            'expiry': 14
        }
    }

    expected = {
        'FSMCLD0000000124': {
            'emails': ['test1@test.com'],
            'expiry': 14
        }
    }
    actual = remove_blocked_email_addresses(expiring, table_name, region)
    assert actual == expected


@mock_aws
def test_remove_blocked_email_addresses_empty_table():
    table_name = 'test_table'
    region = 'us-east-1'
    create_table(table_name, region, 'email')

    expiring = {
        'FSMCLD0000000123': {
            'emails': ['test@test.com'],
            'expiry': 35
        },
        'FSMCLD0000000124': {
            'emails': ['test1@test.com'],
            'expiry': 14
        }
    }

    expected = {
        'FSMCLD0000000123': {
            'emails': ['test@test.com'],
            'expiry': 35
        },
        'FSMCLD0000000124': {
            'emails': ['test1@test.com'],
            'expiry': 14
        }
    }
    actual = remove_blocked_email_addresses(expiring, table_name, region)
    assert actual == expected

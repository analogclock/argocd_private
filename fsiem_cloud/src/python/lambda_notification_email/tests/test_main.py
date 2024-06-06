from json import load
from main import (activation, poc_approval, storage_approval)


def test_activation_correct():
    with open('tests/correct_activation.json', 'r') as f:
        record = load(f)
    environment = 'dev'
    serial_no = record['dynamodb']['NewImage']['serialNumber']['S']
    status = record['dynamodb']['NewImage']['status']['S']
    region = record['dynamodb']['NewImage']['region']['S']
    email = record['dynamodb']['NewImage']['deploymentEmail']['S']
    subject = f'FSIEMCloud {environment}: {serial_no} is {status}'
    message = (
        f'Serial Number: {serial_no}\n'
        f'Environment: {environment}\n'
        f'Region: {region}\n'
        f'Status: {status}\n'
        f'Email: {email}\n'
    )
    expected = subject, message
    actual = activation(record, environment)
    assert actual == expected


def test_activation_playground():
    with open('tests/correct_activation.json', 'r') as f:
        record = load(f)
    environment = 'playground'
    expected = None, None
    actual = activation(record, environment)
    assert actual == expected


def test_poc_approval():
    with open('tests/correct_poc_approval.json', 'r') as f:
        record = load(f)

    environment = 'dev'
    serial_no = record['dynamodb']['NewImage']['serialNumber']['S']
    is_approved = record['dynamodb']['NewImage']['isApproved']['BOOL']

    subject = f'FSIEMCloud {environment}: New POC {serial_no}'
    message = (
        f'Serial Number: {serial_no}\n'
        f'Environment: {environment}\n'
        f'Is Approved: {is_approved}\n'
    )
    expected = subject, message
    actual = poc_approval(record, environment)
    assert actual == expected


def test_storage_approval():
    with open('tests/correct_storage_approval.json', 'r') as f:
        record = load(f)

    environment = 'dev'
    serial_no = record['dynamodb']['NewImage']['serialNumber']['S']
    is_approved = record['dynamodb']['NewImage']['isApproved']['BOOL']

    subject = f'FSIEMCloud {environment}: Storage Reduction {serial_no}'
    message = (
        f'Serial Number: {serial_no}\n'
        f'Environment: {environment}\n'
        f'Is Approved: {is_approved}\n'
    )
    expected = subject, message
    actual = storage_approval(record, environment)
    assert actual == expected

from json import dumps
from main import get_emails


def test_get_emails_permanent_bounce():
    message = {
        "notificationType": "Bounce",
        "bounce": {
            "bounceType": "Permanent",
            "timestamp": "2022-10-18T16:46:18.000Z",
            "bouncedRecipients": [
                {
                    "emailAddress": "test@test.com"
                }
            ]
        }
    }
    event = {
        'Records': [
            {
                'Sns': {
                    'Message': dumps(message),
                }
            }
        ]
    }

    expected = [
        {
            'email': 'test@test.com',
            'type': 'Bounce',
            'timestamp': '2022-10-18T16:46:18.000Z'
        }
    ]
    actual = get_emails(event)
    assert actual == expected


def test_get_emails_transient_bounce():
    message = {
        "notificationType": "Bounce",
        "bounce": {
            "bounceType": "Transient",
            "timestamp": "2022-10-18T16:46:18.000Z",
            "bouncedRecipients": [
                {
                    "emailAddress": "test@test.com"
                }
            ]
        }
    }
    event = {
        'Records': [
            {
                'Sns': {
                    'Message': dumps(message),
                }
            }
        ]
    }

    expected = []
    actual = get_emails(event)
    assert actual == expected


def test_get_emails_complaint():
    message = {
        "notificationType": "Complaint",
        "complaint": {
            "timestamp": "2022-10-18T16:46:18.000Z",
            "complainedRecipients": [
                {
                    "emailAddress": "test@test.com"
                }
            ]
        }
    }
    event = {
        'Records': [
            {
                'Sns': {
                    'Message': dumps(message),
                }
            }
        ]
    }

    expected = [
        {
            'email': 'test@test.com',
            'type': 'Complaint',
            'timestamp': '2022-10-18T16:46:18.000Z'
        }
    ]
    actual = get_emails(event)
    assert actual == expected

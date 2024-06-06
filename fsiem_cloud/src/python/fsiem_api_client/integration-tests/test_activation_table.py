import logging
import pytest
from string import Template
from providers import DynamoDbClientProvider
from fsiem_api_client.activation_table import ActivationTable
from tests.dynamo_db import create_table, delete_table, insert_item
from fsiem_api_client.activation_table import DeploymentMetrics


logging.basicConfig(level=logging.DEBUG)


class TestActivationTable:

    EXAMPLE_ENTRIES = """
    {"serialNumber":"fsiem-prataps--0","created":"2022-06-21T16:37:25.8667909+00:00","deploymentEmail":"prataps@fortinet.com","deploymentSKU":{"archiveStorage":{"endDate":"2023-06-21T16:37:25.6155992+00:00","expiryDays":365,"quantity":1,"startDate":"2022-06-21T16:37:25.6155993+00:00"},"compute":{"endDate":"2023-06-21T16:37:25.6155971+00:00","expiryDays":365,"quantity":1,"startDate":"2022-06-21T16:37:25.6155984+00:00"},"onlineStorage":{"endDate":"2023-06-21T16:37:25.615599+00:00","expiryDays":365,"quantity":1,"startDate":"2022-06-21T16:37:25.6155991+00:00"}},"deploymentType":"va","deploymentWorkerCount":2,"displayRegion":"Europe (Ireland)","ipV4Cidr":"96.45.36.173/32","ipV6Cidr":"::/0","region":"eu-west-1","status":"Complete","url":"https://fsiem-prataps--0.playground.fortisiem.cloud","version":"6.5.0.1511","workersUrl":"https://worker-fsiem-prataps--0.playground.fortisiem.cloud"}
    {"serialNumber":"fsiem-prataps--1","created":"2022-06-21T16:26:40.5040337+00:00","deploymentEmail":"prataps@fortinet.com","deploymentSKU":{"archiveStorage":{"endDate":"2023-06-21T16:26:40.4476001+00:00","expiryDays":365,"quantity":1,"startDate":"2022-06-21T16:26:40.4476002+00:00"},"compute":{"endDate":"2023-06-21T16:26:40.4475997+00:00","expiryDays":365,"quantity":1,"startDate":"2022-06-21T16:26:40.4475998+00:00"},"onlineStorage":{"endDate":"2023-06-21T16:26:40.4475999+00:00","expiryDays":365,"quantity":1,"startDate":"2022-06-21T16:26:40.4476+00:00"}},"deploymentType":"va","deploymentWorkerCount":2,"displayRegion":"US East (N. Virginia)","ipV4Cidr":"96.45.36.173/32","ipV6Cidr":"::/0","region":"us-east-1","status":"LicenseInProgress","url":"https://fsiem-prataps--1.playground.fortisiem.cloud","workersUrl":"https://worker-fsiem-prataps--1.playground.fortisiem.cloud"}
    {"serialNumber":"fsiem-omandryc-1","created":"2022-06-20T23:33:15.7581577+00:00","deploymentEmail":"omandrychenko@fortinet.com","deploymentSKU":{"archiveStorage":{"endDate":"2023-06-20T23:33:15.7542221+00:00","expiryDays":365,"quantity":1,"startDate":"2022-06-20T23:33:15.7542222+00:00"},"compute":{"endDate":"2023-06-20T23:33:15.7542218+00:00","expiryDays":365,"quantity":1,"startDate":"2022-06-20T23:33:15.7542219+00:00"},"onlineStorage":{"endDate":"2023-06-20T23:33:15.754222+00:00","expiryDays":365,"quantity":1,"startDate":"2022-06-20T23:33:15.754222+00:00"}},"deploymentType":"va","deploymentWorkerCount":2,"displayRegion":"US East (N. Virginia)","ipV4Cidr":"0.0.0.0/0","ipV6Cidr":"::/0","region":"us-east-1","status":"SetupInProgress","url":"https://fsiem-omandryc-1.playground.fortisiem.cloud","version":"6.5.0.1511","workersUrl":"https://worker-fsiem-omandryc-1.playground.fortisiem.cloud"}
    {"serialNumber":"fsiem-omandryc-0","created":"2022-06-21T18:34:20.1963815+00:00","deploymentEmail":"omandrychenko@fortinet.com","deploymentSKU":{"archiveStorage":{"endDate":"2023-06-21T18:34:20.0565451+00:00","expiryDays":365,"quantity":1,"startDate":"2022-06-21T18:34:20.0565453+00:00"},"compute":{"endDate":"2023-06-21T18:34:20.0564109+00:00","expiryDays":365,"quantity":1,"startDate":"2022-06-21T18:34:20.0564552+00:00"},"onlineStorage":{"endDate":"2023-06-21T18:34:20.056544+00:00","expiryDays":365,"quantity":1,"startDate":"2022-06-21T18:34:20.056545+00:00"}},"deploymentType":"va","deploymentWorkerCount":2,"displayRegion":"US East (N. Virginia)","ipV4Cidr":"0.0.0.0/0","ipV6Cidr":"::/0","region":"us-east-1","status":"Complete","url":"https://fsiem-omandryc-0.playground.fortisiem.cloud","version":"6.5.0.1511","workersUrl":"https://worker-fsiem-omandryc-0.playground.fortisiem.cloud"}
    {"serialNumber": "FSMCLD0000000154", "archiveSizeUsage": 6144, "created": "2022-08-10T23:50:39.5536078+00:00", "deploymentEmail": "omandrychenko@fortinet.com", "deploymentSKU": { "archiveStorage": { "endDate": "2023-08-08T00:00:00+00:00", "expiryDays": 363, "quantity": 1, "startDate": "2022-08-08T00:00:00+00:00" }, "compute": { "endDate": "2023-08-08T00:00:00+00:00", "expiryDays": 363, "quantity": 5, "startDate": "2022-08-08T00:00:00+00:00" }, "onlineStorage": { "endDate": "2023-08-08T00:00:00+00:00", "expiryDays": 363, "quantity": 1, "startDate": "2022-08-08T00:00:00+00:00" } }, "deploymentType": "va", "displayRegion": "US East (N. Virginia)", "ipV4Cidr": "0.0.0.0/0", "ipV6Cidr": "::/0", "onlineSizeUsage": 50720768, "preventUpdate": true, "preventUpdateReason": "OM manual testing", "region": "us-east-1", "status": "Complete", "storageType": "clickhouse", "url": "https://fsmcld0000000154.playground.fortisiem.cloud", "version": "6.6.0.1633", "workersUrl": "https://worker-fsmcld0000000154.playground.fortisiem.cloud"}
    {"serialNumber": "FSMCLD0000000155"}
    """  # noqa

    INSERT_CMD = Template('INSERT INTO $table VALUE $value')

    def insert_test_data(self, table_name: str, table_region: str):
        for entry in filter(None, self.EXAMPLE_ENTRIES.strip().split('\n')):
            # DynamoDb doesn't understand double quote, replace with single
            entry = entry.replace('"', '\'')
            stmt = self.INSERT_CMD.substitute(table=table_name, value=entry)
            insert_item(table_region, stmt)

    @pytest.fixture(scope="class")
    def temp_table(self):
        """Create a real temp table and fill it with some real-looking data.
        After all test finish running, this method will delete the table.
        Teardown happens after the yield keyword.
        """
        tables = DynamoDbClientProvider.tables()
        for t in tables:
            # Test fixture setup
            print(f'Creating {t.table} in {t.region} for test purposes')
            if 'integration_test' not in t.table:
                raise RuntimeError(
                    'Table name must include `integration_test`. Integration '
                    'tests will NOT run to avoid modifying real data tables.')

            # Helps when previous test run didn't delete a table
            try:
                create_table(t.table, t.region, True)
            except Exception:
                delete_table(t.table, t.region, True)
                create_table(t.table, t.region, True)

            print("Inserting fake data")
            self.insert_test_data(t.table, t.region)

            # Run the tests - yield returns to the test function
            yield t

            # Test fixture teardown
            print(f'Deleting {t.table} in {t.region}')
            delete_table(t.table, t.region, True)

    def test_get_status(self, temp_table: ActivationTable):
        sn = 'fsiem-omandryc-1'
        assert temp_table.get_status(sn) == 'SetupInProgress'
        assert temp_table.get_status('does not exist') is None

    def test_update_status(self, temp_table: ActivationTable):
        sn = 'fsiem-omandryc-1'

        temp_table.update_status(sn, 'foo')
        assert temp_table.get_status(sn) == 'foo'

        temp_table.update_status(sn, 'SetupInProgress')
        assert temp_table.get_status(sn) == 'SetupInProgress'

    def test_get_all_items(self, temp_table: ActivationTable):
        items = temp_table.get_all_items(limit=1)
        assert len(items) == 5

        items = temp_table.get_all_items()
        assert len(items) == 5

    def test_get_deployment_region(self, temp_table: ActivationTable):
        sn = 'fsiem-omandryc-1'
        assert temp_table.get_deployment_region(sn) == 'us-east-1'

    def test_update_version(self, temp_table: ActivationTable):
        sn = 'fsiem-omandryc-1'

        temp_table.update_version(sn, 'version-12345')

        items = temp_table.get_all_items()
        actual = next(x for x in items if x['serialNumber']['S'] == sn)
        assert actual['version']['S'] == 'version-12345'

        temp_table.update_version(sn, '6.5.0.1511')

    def test_update_usage_size(self, temp_table: ActivationTable):
        sn = 'fsiem-omandryc-1'

        temp_table.update_usage_size(temp_table.online_storage, sn, 100)

        items = temp_table.get_all_items()
        actual = next(x for x in items if x['serialNumber']['S'] == sn)
        assert int(actual['onlineSizeUsage']['N']) == 100

    def test_storage_type(self, temp_table: ActivationTable):
        sn = 'FSMCLD0000000154'
        assert temp_table.get_storage_type(sn) == 'clickhouse'
        temp_table.set_storage_type(sn, 'foo')
        assert temp_table.get_storage_type(sn) == 'foo'

    def test_prevent_update(self, temp_table: ActivationTable):
        sn = 'FSMCLD0000000154'
        assert temp_table.get_prevent_update(sn)
        temp_table.set_prevent_update(sn, False)
        assert not temp_table.get_prevent_update(sn)

    def test_prevent_update_reason(self, temp_table: ActivationTable):
        sn = 'FSMCLD0000000154'
        assert temp_table.get_prevent_update_reason(sn) == 'OM manual testing'
        temp_table.set_prevent_update_reason(sn, 'foo')
        assert temp_table.get_prevent_update_reason(sn) == 'foo'

    def test_deployment_metrics(self, temp_table: ActivationTable):
        sn = 'FSMCLD0000000154'
        assert temp_table.get_deployment_metrics(sn) is None
        expected = DeploymentMetrics('s3_bucket', 'dir', 1000, 10)
        temp_table.set_deployment_metrics(sn, expected)
        actual = temp_table.get_deployment_metrics(sn)
        assert actual == expected

    def test_deployment_updatesku(self, temp_table: ActivationTable):
        sn = 'FSMCLD0000000154'
        full_item = temp_table.get_full_item(sn)
        assert full_item is not None
        new_sku = {
            'compute': {
                'quantity': 100
            }
        }
        assert temp_table.update_sku(sn, new_sku) is None

    def test_get_emails(self, temp_table: ActivationTable):
        sn = 'FSMCLD0000000154'
        assert temp_table.get_deployment_region(sn) == 'us-east-1'

    def test_get_version(self, temp_table: ActivationTable):
        sn = 'FSMCLD0000000154'
        assert temp_table.get_version(sn) == '6.6.0.1633'

        sn = 'FSMCLD0000000155'
        assert not temp_table.get_version(sn)

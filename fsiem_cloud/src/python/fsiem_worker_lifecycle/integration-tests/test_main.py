from main import LifecycleHandler

cluster_region = 'us-east-1'
portal_region = 'us-east-1'
sn = 'FSMCLD0000123'
env = 'playground'
instance_id = 'id-1234'
s3_bucket = 'fsiem_test'
s3_region = 'us-east-1'
super_url = 'fsmcld0000123.playground.fortisiem.cloud'
secret_vm_dict = {
    '123': '123'
}
cognito_url = 'https://test.cognito'


class TestLifecycleHandler:

    uut = LifecycleHandler(
        cluster_region, portal_region, sn, env, instance_id, s3_bucket,
        s3_region, super_url, secret_vm_dict, cognito_url)

    def test_get_instance_info(self):
        self.uut._get_instance_info()

    def test_run_automation(self):
        self.uut._run_automation('doc_123', '1234-5678', 'fsiem-automation')

from main import main

sn = 'FSMCLD0000000193'
region = 'eu-west-1'
ddb_region = 'us-east-1'


def test_main():
    main(sn, region, 100, 20, 'fsiem_external_storage_table_playground',
         ddb_region, 'fsiem_external_storage_status_table_playground')

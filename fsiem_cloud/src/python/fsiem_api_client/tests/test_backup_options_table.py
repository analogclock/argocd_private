from fsiem_api_client.backup_options_table import BackupOptions


def test_BackupOptions_from_str():
    payload = """[{"S3_COMPRESSION_LEVEL": "1"}, {"S3_COMPRESSION_FORMAT": "tar"}, {"S3_USE_CUSTOM_STORAGE_CLASS": "false"}]""" # noqa
    options = BackupOptions()

    assert len(list(options.from_str(None))) == 0
    assert len(list(options.from_str(""))) == 0
    assert len(list(options.from_str("[]"))) == 0

    items = options.from_str(payload)
    for key, value in items:
        assert key
        assert value

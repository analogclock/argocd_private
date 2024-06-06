from fsiem_api_client.gzip_compress import GzipCompress

uut = GzipCompress()
input_string = "This is a sample string to compress with gzip."


class TestGzipCompress:

    def test_compress(self):
        b = uut.compress_str(input_string)
        assert b

    def test_decompress(self):
        b = uut.compress_str(input_string)
        output_string = uut.decompress_str(b)
        assert input_string == output_string

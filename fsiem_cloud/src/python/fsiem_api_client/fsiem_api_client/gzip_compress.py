import gzip


class GzipCompress:

    def compress_str(self, input_string: str) -> bytes:
        input_bytes = input_string.encode('utf-8')
        return gzip.compress(input_bytes)

    def decompress_str(self, input_bytes: bytes) -> str:
        output_bytes = gzip.decompress(input_bytes)
        return output_bytes.decode('utf-8')

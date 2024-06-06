import re

from fsiem_api_client.const import FsiemInstanceRole
from fsiem_api_client.string_utils import \
    contains_subset_ascii

# Regex to validate disk file size, it means:
# - use ascii and ignore case
# - starts with numbers
# - followed by any b (for byte), k (for kilobyte), etc.
# These works: 25G, 25Gi, 5TB. These won't work: foo, 4E.
SIZE_REGEX = re.compile(r'^\d+[bkmgtpi]+$', re.ASCII | re.IGNORECASE)


class Validator:

    def is_valid_role(self, role: str) -> bool:
        """Check if role is strictly valid role.

        Parameters
        ----------
        role : str
            FSIEM role

        Returns
        -------
        bool
            True if role is known and valid, otherwise false
        """
        return role in [
            FsiemInstanceRole.super.name,
            FsiemInstanceRole.worker.name,
            FsiemInstanceRole.keeper.name,
            FsiemInstanceRole.ingestion.name
        ]

    def enforce_valid_role(self, role: str):
        """Throw ValueError if the argument is invalid"""
        if not role:
            raise ValueError('Invalid argument')
        if not self.is_valid_role(role):
            raise ValueError(f'Invalid argument: {role}')

    def are_valid_disk_sizes(self, disk_sizes: []) -> bool:
        """Check if disk sizes look valid

        Parameters
        ----------
        disk_sizes : list
            List of disk sizes, like ['100G']

        Returns
        -------
        bool
            True if the argument matches valid size regex for every element
        """
        result = any([x for x in disk_sizes if re.match(SIZE_REGEX, x)])
        return result

    def enforce_valid_disk_sizes(self, disk_sizes: []):
        """Throw ValueError if the argument is invalid"""
        if not disk_sizes:
            raise ValueError('Invalid argument')
        if not self.are_valid_disk_sizes(disk_sizes):
            raise ValueError(f'Invalid argument: {disk_sizes}')

    def is_valid_memory_size(self, size: str) -> bool:
        """Check if memory size looks valid

        Parameters
        ----------
        size : str
            Memory size, e.g. 5120m

        Returns
        -------
        bool
            True if the argument matches valid size regex
        """
        return re.match(SIZE_REGEX, size)

    def enforce_valid_memory_size(self, size: str):
        """Throw ValueError if the argument is invalid"""
        if not size:
            raise ValueError('Invalid argument')
        if not self.is_valid_memory_size(size):
            raise ValueError(f'Invalid argument: {size}')

    def is_single_sql_statement(self, sql: str) -> bool:
        """Check if SQL is one statement or multiple statement. This method
        looks for a semicolon symbol in the SQL.

        Parameters
        ----------
        sql : str
            SQL statement

        Returns
        -------
        bool
            True if SQL string is a single statement
        """
        return not (";" in sql)

    def enforce_single_sql_statement(self, sql: str):
        """Throw ValueError if the argument is invalid"""
        if not sql:
            raise ValueError('Invalid argument')
        if not self.is_single_sql_statement(sql):
            raise ValueError(f'Invalid argument: {sql}')

    def enforce_subset_ascii(self, s: str):
        """Throw ValueError if the argument is invalid"""
        if not s:
            raise ValueError('Invalid argument')
        if not contains_subset_ascii(s):
            raise ValueError(f'Invalid argument: {s}')

    def enforce_int(self, input_value: int):
        """Throw ValueError if the argument is not an integer"""
        if not isinstance(input_value, int):
            raise ValueError(f'Invalid argument: {input_value}')

    def enforce_dict_subset_ascii(self, input: dict):
        """Throw ValueError if the argument is invalid"""
        if not input:
            raise ValueError('Invalid argument')
        for k, v in input.items():
            if not contains_subset_ascii(k):
                raise ValueError(f'Invalid argument: {k}')
            # Value can be of different type, like int, to validate it
            # first convert it to string
            if not contains_subset_ascii(str(v)):
                raise ValueError(f'Invalid argument: {v}')

    def enforce_list_subset_ascii(self, input: list[str]):
        """Throw ValueError if the argument is invalid"""
        if not input:
            raise ValueError('Invalid argument')
        for v in input:
            # Value can be of different type, like int, to validate it
            # first convert it to string
            if not contains_subset_ascii(str(v)):
                raise ValueError(f'Invalid argument: {v}')

    def is_valid_s3_bucket_name(self, bucket_name):
        # https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html
        # Check length between 3 and 63 characters long
        if not (3 <= len(bucket_name) <= 63):
            return False

        # Check only lowercase letters, numbers, dots (.), and
        # hyphens (-) allowed
        if not re.match("^[a-z0-9.-]+$", bucket_name):
            return False

        # Check if the bucket name starts and ends with a letter or number
        if not (bucket_name[0].isalnum() and bucket_name[-1].isalnum()):
            return False

        # Check consecutive periods
        if ".." in bucket_name:
            return False

        # Check if the bucket name starts or ends with a period
        if bucket_name.startswith('.') or bucket_name.endswith('.'):
            return False

        # Check if the bucket name starts or ends with a hyphen
        if bucket_name.startswith('-') or bucket_name.endswith('-'):
            return False

        return True

    def is_valid_s3_bucket_prefix(self, bucket_prefix):
        # Check allowed characters in the prefix
        if not re.match("^[a-zA-Z0-9./_-]+$", bucket_prefix):
            return False

        return True

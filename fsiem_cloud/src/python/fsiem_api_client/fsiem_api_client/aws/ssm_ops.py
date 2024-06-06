import json
import re
import random
from math import ceil
from fsiem_api_client.aws.ec2 import Ec2
from fsiem_api_client.deployment_metrics import DfResponse, DfResponseItem
from fsiem_api_client.aws.ssm import TIMEOUT_1_HOUR_IN_SECONDS, \
    TIMEOUT_23_HOURS_IN_SECONDS, Ssm, SsmCmdResponse
from fsiem_api_client.const import BackupListItem, BackupType, \
    FsiemInstanceRole
from fsiem_api_client.gzip_compress import GzipCompress
from fsiem_api_client.validator import Validator


validator = Validator()


class SsmOps:
    """
    Wrapper class around AWS SSM operations used by the setup container.
    E.g. you can use this to locate disks suitable for ClickHouse deployment.
    """

    def __init__(self, region: str, sn: str) -> None:
        if not region:
            raise ValueError('region is not defined')
        if not sn:
            raise ValueError('sn is not defined')
        self.sn = sn
        self.ssm = Ssm(region)
        self.ec2 = Ec2(region)

    def _parse_lsblk_response(self, j: str, disk_size: str) -> list:
        """Parse lsblk json response and extract a list of disks paths"""
        parsed_json = json.loads(j)
        block_devices = parsed_json['blockdevices']
        result = []
        for disk in block_devices:
            if disk['size'] == disk_size:
                result.append(disk['name'])
        return result

    def _parse_lsblk_response_except(self, j: str, disk_sizes: list) \
            -> list:
        """Parse lsblk json response and extract a list of disks paths.

        This method will exclude disks with the provided size. This is useful
        when we know the sizes of root volume and other volumes, and want to
        find other disks of arbitrary size.
        """
        parsed_json = json.loads(j)
        block_devices = parsed_json['blockdevices']
        result = []
        for disk in block_devices:
            if disk['size'] not in disk_sizes:
                result.append(disk['name'])
        return result

    def _lsblk(self, instance_id: str) -> SsmCmdResponse:
        """
            Execute this command on the remote EC2 instance:
                lsblk --output NAME,SIZE --paths --json
        """
        if not instance_id:
            raise ValueError('Instance id not provided')
        cmd = 'lsblk --output NAME,SIZE --paths --json'
        return self.ssm.exec_command(instance_id, cmd)

    def _find_disks_except_given_sizes(self, instance_id: str,
                                       disk_sizes: list) -> list:
        """Execute 'lsblk' call on a remote machine. Then parse response
        to locate disks with the sizes other than the specified `disk_sizes`.

        This is useful when we know static disks' sizes and want to get a
        list of disks with other sizes. E.g. we know the size of opt, svn,
        root volumes, get the volumes for ClickHouse database.

        Parameters
        ----------
        instance_id : str
            AWS EC2 instance id
        disk_sizes : list
            A list of disk with known sizes ['25GB', '60GB']

        Returns
        -------
        list
            A list of local disks with different size to the provided sizes
        """
        if not instance_id:
            raise ValueError('Instance id not provided')

        # Safeguard against injection attack
        validator.enforce_valid_disk_sizes(disk_sizes)

        resp = self._lsblk(instance_id)
        return self._parse_lsblk_response_except(resp.output, disk_sizes)

    def _list_disks(self, role: str) -> str:

        # Safeguard against injection attack
        validator.enforce_valid_role(role)

        ids = self.ec2.get_instance_ids(self.sn, role)
        resp = {}
        cmd_id = self.ssm.send_cmd(ids, [
            '(lsblk --output NAME,SIZE,TYPE --paths -n | grep disk)'])
        for id in ids:
            cmd_resp = self.ssm.get_output(id, cmd_id)
            output = re.sub(' +', ' ', cmd_resp.output)
            output = output.replace('\n', ', ').strip(', ')
            resp[id] = output
        return resp

    def _find_disks(self, role: str, disks_of_known_sizes: list) -> dict:

        # Safeguard against injection attack
        validator.enforce_valid_role(role)
        validator.enforce_valid_disk_sizes(disks_of_known_sizes)

        ids = self.ec2.get_instance_ids(self.sn, role)
        resp = {}
        for id in ids:
            disk_paths = self._find_disks_except_given_sizes(
                id, disks_of_known_sizes)
            resp[id] = disk_paths
        return resp

    def _parse_df_resp(self, df: str, size_unit='G') -> list[DfResponseItem]:
        if not df:
            raise ValueError('Cannot parse an empty df response')
        lines = df.splitlines()

        result = []
        # Skip header line
        for line in lines[1:]:
            splits = line.split()
            item = DfResponseItem(
                device=splits[0],
                size_unit=size_unit,
                total_size=int(splits[1].replace(size_unit, '')),
                used_size=int(splits[2].replace(size_unit, '')),
                available_size=int(splits[3].replace(size_unit, '')),
                capacity_utilization=splits[4],
                mount_point=splits[5])
            result.append(item)
        return result

    def _clickhouse_clients_exec_unsafe(self, instance_id: list[str],
                                        sql_query: str) \
            -> list[SsmCmdResponse]:
        """Execute ClickHouse query on many worker nodes.

        The only check that is performed is that SQL string contains only
        a single query/statement. This is NOT safe to guard against SQL
        injection.

        DO NOT use this method with user-provided input. You can use this
        where SQL statement is hardcoded and doesn't have any input in to
        the statement itself.

        Returns
        -------
        list[SsmCmdResponse]
            List of response object from many clickhouse nodes
        """
        if not instance_id:
            raise ValueError('Instance id not provided')
        validator.enforce_subset_ascii(sql_query)
        validator.enforce_single_sql_statement(sql_query)

        # You can only run a single query
        # everything after the semicolon is ignored.
        query = f'clickhouse-client --query="{sql_query}"'
        print(f'Executing clickhouse query on {instance_id}, query: {query}')
        return self.ssm.exec_commands(instance_id, [query])

    def _split_partition_into_2_chunks(self, partition: str) -> []:
        """Split partition key into two sub-parts.
        This assumes a strict partition key format used in the
        fsiem.events_replicated table.
        Example input:
            (18250,20231201)
        Example output: 18250 20231201

        Parameters
        ----------
        self : _type_
            SSM ops instance
        partition : str
            Partition value
        """
        if not partition:
            raise ValueError('Partition not provided')
        # Regex to capture two groups:
        # Opening (
        # Group 1 to find any digits any number of times
        # Comma , and no or one space
        # Group 2 to find any digits any number of times
        # Closing )
        reg_exp = r"\((\d.*),\s?(\d.*)\)"
        result = re.search(reg_exp, partition)
        if not result:
            raise ValueError(f'Invalid partition value: {partition}')

        groups = result.groups()
        if not groups or len(groups) != 2 or \
                not int(result.group(1)) or not int(result.group(2)):
            raise ValueError(f'Invalid partition value: {partition}')
        return groups

    def get_app_server_memory(self, filename: str) -> dict:
        """Retrieve the App Servers current memory setting

        Parameters
        ----------
        filename : str
            The name of the xml file where the JVM memory is set

        Returns
        -------
        dict
            A dictionary: key is instance id, value the command output
            E.g.:
            {
                'i-02c3e33af3f7f4530':
                '        <jvm-options>-Xms10240m</jvm-options>'
            }
        """
        # Safeguard against injection attack
        validator.enforce_subset_ascii(filename)

        ids = self.ec2.get_instance_ids(self.sn, FsiemInstanceRole.super.name)
        cmd_id = self.ssm.send_cmd(ids, [
            f'(cat {filename} | grep Xms)'])
        resp = {}
        for id in ids:
            cmd_resp = self.ssm.get_output(id, cmd_id)
            resp[id] = cmd_resp.output
        return resp

    def update_app_server_memory(self, instance_ids: list, current_memory: str,
                                 new_memory: str, filename: str) -> dict:
        """Update the XML file containing the JVM settings with the memory
        settings from the compute map

        Parameters
        ----------
        instance_ids : list
            The instance IDs of the instances to be updated
        current_memory : str
            The current memory set, i.e.: 5120m
        new_memory : str
            The new memory setting to insert, i.e.: 10240m
        filename : str
            The name of the xml file where the JVM memory is set

        Returns
        -------
        dict
            A dictionary: key is instance id, value the command output
        """
        # Safeguard against injection attack
        if not instance_ids:
            raise ValueError('Instance id not provided')
        validator.enforce_valid_memory_size(current_memory)
        validator.enforce_valid_memory_size(new_memory)
        validator.enforce_subset_ascii(filename)

        cmd_id = self.ssm.send_cmd(instance_ids, [
            f'(sed -i \'s/{current_memory}/{new_memory}/g\' {filename})'])
        resp = {}
        for id in instance_ids:
            cmd_resp = self.ssm.get_output(id, cmd_id)
            resp[id] = cmd_resp.output
        return resp

    def stop_app_server(self, instance_ids: list) -> dict:
        """Stop the app server process. It will automatically come back online
        and pick up the updated memory settings

        Parameters
        ----------
        instance_ids : list
            The instance IDs of the instances to be updated

        Returns
        -------
        dict
            A dictionary: key is instance id, value the command output
        """
        if not instance_ids:
            raise ValueError('Instance id not provided')

        cmd_id = self.ssm.send_cmd(instance_ids, [
            '(/opt/glassfish/bin/asadmin stop-domain domain1 )'])
        resp = {}
        for id in instance_ids:
            cmd_resp = self.ssm.get_output(id, cmd_id)
            resp[id] = cmd_resp.output
        return resp

    def list_disks_on_supers(self) -> dict:
        """Get a dictionary of disks for every supper node

        Returns
        -------
        dict
            A dictionary: key is instance id, value is lsblk output
            E.g.:
            {
                'i-02c3e33af3f7f4530':
                '/dev/nvme3n1 100G disk, /dev/nvme1n1 60G disk, ...'
            }
        """
        return self._list_disks(FsiemInstanceRole.super.name)

    def list_disks_on_workers(self) -> dict:
        """Get a dictionary of disks for every worker node

        Returns
        -------
        dict
            A dictionary: key is instance id, value is lsblk output
            E.g.:
            {
                'i-02c3e33af3f7f4530':
                '/dev/nvme3n1 100G disk, /dev/nvme1n1 60G disk, ...'
            }
        """
        return self._list_disks(FsiemInstanceRole.worker.name)

    def get_number_of_workers(self) -> int:
        """Get the number of workers"""
        return len(self.ec2.get_instance_ids(
            self.sn, FsiemInstanceRole.worker.name))

    def get_number_of_supers(self) -> int:
        """Get the number of supers"""
        return len(self.ec2.get_instance_ids(
            self.sn, FsiemInstanceRole.super.name))

    def get_number_of_keepers(self) -> int:
        """Get the number of keepers"""
        return len(self.ec2.get_instance_ids(
            self.sn, FsiemInstanceRole.keeper.name))

    def find_disks_supers(self, disks_of_known_sizes: list) -> dict:
        """Find disks paths for every supper node, excluding system disks

        Returns
        -------
        dict
            A dictionary: key is instance id, value is array of disks
            {'i-02c3e33af3f7f4530': ['/dev/nvme1n1', '/dev/nvme2n1']}
        """
        # Safeguard against injection attack
        validator.enforce_valid_disk_sizes(disks_of_known_sizes)

        return self._find_disks(FsiemInstanceRole.super.name,
                                disks_of_known_sizes)

    def find_disks_workers(self,  disks_of_known_sizes: list) -> dict:
        """Find disks paths for every worker node, excluding system disks

        Returns
        -------
        dict
            A dictionary: key is instance id, value is array of disks
            {'i-02c3e33af3f7f4530': ['/dev/nvme1n1', '/dev/nvme2n1']}
        """
        # Safeguard against injection attack
        validator.enforce_valid_disk_sizes(disks_of_known_sizes)

        return self._find_disks(FsiemInstanceRole.worker.name,
                                disks_of_known_sizes)

    def get_instance_info(self, role: str, disks_of_known_sizes: list) -> list:
        """Get instance info with local OS disks paths, excluding system disks

        Parameters
        ----------
        role: str
            Instance role, super or worker
        disks_of_known_sizes: list
            Ignore these disks

        Returns
        -------
        list
            A list of instance info with ClickHouse disks found
            by the specified size, e.g.:
            [
                {
                    'InstanceId': 'i-0ec575a2459b51d26',
                    'InstanceType': 'c6i.xlarge',
                    'PrivateDnsName': 'ip-10-0-102-145.ec2.internal',
                    'ClickHouseDiskPaths': ['/dev/nvme2n1']
                    ... - other instance info
                }
            ]
        """
        # Safeguard against injection attack
        validator.enforce_valid_role(role)
        validator.enforce_valid_disk_sizes(disks_of_known_sizes)

        infos = self.ec2.get_instance_info(self.sn, role)
        for info in infos:
            disk_paths = self._find_disks_except_given_sizes(
                info['InstanceId'], disks_of_known_sizes)
            kv = {'ClickHouseDiskPaths': disk_paths}
            # E.g. append { 'ClickHouseDiskPaths' : ['/dev/nvme2n1'] }
            info.update(kv)
        return infos

    def get_instance_info_id(self, instance_id: str,
                             disks_of_known_sizes: list) -> list:
        """Get instance info with local OS disks paths, excluding system disks

        Parameters
        ----------
        instance_id: str
            The Id of the target instance
        disks_of_known_sizes: list
            Ignore these disks

        Returns
        -------
        list
            A list of instance info with ClickHouse disks found
            by the specified size, e.g.:
            [
                {
                    'InstanceId': 'i-0ec575a2459b51d26',
                    'InstanceType': 'c6i.xlarge',
                    'PrivateDnsName': 'ip-10-0-102-145.ec2.internal',
                    'ClickHouseDiskPaths': ['/dev/nvme2n1']
                    ... - other instance info
                }
            ]
        """
        infos = self.ec2.get_instance_info_from_id(instance_id)
        for info in infos:
            disk_paths = self._find_disks_except_given_sizes(
                info['InstanceId'], disks_of_known_sizes)
            kv = {'ClickHouseDiskPaths': disk_paths}
            # E.g. append { 'ClickHouseDiskPaths' : ['/dev/nvme2n1'] }
            info.update(kv)
        return infos

    def get_workers_used_disk_space(self,
                                    disks_of_known_sizes: list) -> DfResponse:
        """Get used disk space for ClickHouse disks in GB. This is
        intended to be shown in UI. The calculations run like this:

        Sum total used disk space in bytes on workers for ClickHouse disks,
        divide by the number of workers (to account for replication),
        math-ceiling the result to a nearest byte.

        Returns
        -------
        DfResponse
            Online storage metrics
        """
        # Safeguard against injection attack
        validator.enforce_valid_disk_sizes(disks_of_known_sizes)

        instance_disks = self.find_disks_workers(disks_of_known_sizes)
        number_of_workers = self.get_number_of_workers()
        if number_of_workers == 0:
            raise ValueError('Number of workers cannot be 0')
        # units are bytes
        result = DfResponse(size_unit='b')
        for id in instance_disks:
            # --block-size=1 means it's bytes, rather than default 1Kb
            resp = self.ssm.exec_command(id, 'df --portability --block-size=1')
            df_items = self._parse_df_resp(resp.output, size_unit='b')
            disks = instance_disks[id]
            for row in df_items:
                if row.device in disks:
                    # Only keep track of ClickHouse disks, ignore other disks
                    result.total_size += row.used_size
                    result.items.append(row)
        result.total_size = ceil(result.total_size / number_of_workers)

        print(f'Online metrics: {result}')
        return result

    def clickhouse_archive_size(self) -> int:
        """Get ClickHouse archive storage size in bytes.
        Queries every worker in parallel and sums up the result. CH query is:

            SELECT sum(bytes_on_disk)
            FROM system.parts
            WHERE disk_name='archive'

        Result is divided by the number of workers to account for replication.

        Returns
        -------
        int
            ClickHouse archive disk sizes in bytes combined for all workers
        """
        sql = """
            SELECT sum(bytes_on_disk)
            FROM system.parts
            WHERE disk_name={p0:String}
        """.replace('\n', '')
        query = f'''
            clickhouse-client
                --param_p0="archive"
                --query="{sql}"
        '''.replace('\n', '')
        total = 0
        number_of_workers = self.get_number_of_workers()
        if number_of_workers == 0:
            raise ValueError('Number of workers cannot be 0')
        worker_ids = self.workers_instance_id()
        if not worker_ids:
            raise ValueError('Instance id not provided')
        responses = self.ssm.exec_commands(worker_ids, [query])
        for resp in responses:
            size = int(resp.output)
            total += size
            print(f'Instance {resp.instance_id} uses {size} bytes in S3')

        result = ceil(total / number_of_workers)
        print(f'Archive size {result}, ({total} div by {number_of_workers})')
        return result

    def workers_instance_id(self) -> list[str]:
        """Get all workers EC2 instance infos for a given Serial Number"""
        return list(map(lambda x: x['InstanceId'],
                        self.ec2.get_instance_info(
                            self.sn, FsiemInstanceRole.worker.name)))

    def worker_instance_id_by_dns(self, instance_dns: str) -> str:
        """The the ID of the ec2 instance using the private DNS

        Parameters
        ----------
        instance_dns : str
            Private DNS name of the instance

        Returns
        -------
        str
            Instance ID
        """
        if not instance_dns:
            raise ValueError('Instance dns not provided')

        instances = self.ec2.get_instance_info(
            self.sn, FsiemInstanceRole.worker.name)
        for instance in instances:
            if instance['PrivateDnsName'] == instance_dns:
                return instance['InstanceId']
        return ''

    def clickhouse_oldest_data(self) -> dict[str, int]:
        """Get a dictionary of 100 oldest {partition_name -> size} from each
        node, then combine into an aggregated cluster result

        Returns
        -------
        dict[str: int]
            A dictionary of partition name and its size.
            Key - partition name, value - size of data in bytes. Example:
            {'(18250,20221129)': 986320, '(18250,20221130)': 98247010316}
        """
        sql = r"""
            SELECT
                partition,
                extract(partition, '\(\d+,(\d+)\)') as daily_bucket,
                sum(bytes_on_disk),
                formatReadableSize(sum(bytes_on_disk))
            FROM
                system.parts
            WHERE
                table = {tbl:String}
                and active
                and disk_name = {disk:String}
            GROUP BY partition
            ORDER BY daily_bucket ASC
            LIMIT 100
            FORMAT JSON
        """.replace('\n', '')
        query = f'''
            clickhouse-client
                --param_tbl="events_replicated"
                --param_disk="archive"
                --query="{sql}"
        '''.replace('\n', '')
        worker_ids = self.workers_instance_id()
        if not worker_ids:
            raise ValueError('Instance id not provided')
        responses = self.ssm.exec_commands(worker_ids, [query])
        result = {}
        for resp in responses:
            print(f'Instance {resp.instance_id}: {resp}')
            output = json.loads(resp.output)
            for item in output['data']:
                partition = item['partition']
                size = int(item['sum(bytes_on_disk)'])
                result[partition] = size
        return result

    def clickhouse_count_external_storage_records(self,
                                                  org_id: int,
                                                  partitions: list[str]
                                                  ) -> list:
        """_Count of records in the archive partition_

        Parameters
        ----------
        org_id : int
            _organization id_
        partitions : list[str]
            _a list of partition name_
            example:
            ['(18250,20221129)', '(18250,20221130)']

        Returns
        -------
        list
            _Response to the ssm exec command_
        """

        print(f'Organization Id: {org_id}')
        print(f'Partition values where disk_name is archive: {partitions}')

        # Safeguard against injection attack
        validator.enforce_int(org_id)
        validator.enforce_list_subset_ascii(partitions)

        worker_id = random.choice(self.workers_instance_id())
        print(f'Worker instance id: {worker_id}')
        # Create the database query
        # If org_id is '-1' we want to get all records with all cust ids
        # If we have actual cust id, then use it to restrict the result set.
        org_clause = "" if org_id == -1 \
            else f"AND phCustId = {org_id}"

        query = f"""
              SELECT
                 count(*)
              FROM
                 fsiem.events_replicated
              WHERE
                  _partition_value IN ({', '.join(partitions)})
                  {org_clause}
        """
        cmd = f'clickhouse-client --query "{query}" '
        return self.ssm.exec_command(worker_id, cmd)

    def clickhouse_copy_to_external_storage(self, org_id: int,
                                            external_storage: str,
                                            partitions: list[str],
                                            file_name: str,
                                            file_format: str) -> list:
        """_Copy data from archive partition to external storage s3 bucket_

        Parameters
        ----------
        org_id : int
            _organization id_
        external_storage : str
            _s3 bucket name used to copy the data_
        partitions : list[str]
            _a list of partition names_
            example:
            ['(18250,20221129)', '(18250,20221130)']
        file_name : str
            _name of the file with external storage data_
        file_format : str
            _format of the file in which external storage file is copied_

        Returns
        -------
        list
            _Response to the ssm exec command_

        Raises
        ------
        ValueError
            _Response to the ssm exec command_
        """

        print('Copying oldest data to external storage')
        print(f'Organization Id: {org_id}')
        print(f'Customer provided external storage: {external_storage}')

        # Safeguard against injection attack
        validator.enforce_int(org_id)
        validator.enforce_subset_ascii(external_storage)
        validator.enforce_list_subset_ascii(partitions)
        validator.enforce_subset_ascii(file_name)
        validator.enforce_subset_ascii(file_format)

        # Check if the bucket name ends with '/' otherwise add '/' at the end
        if not external_storage.endswith('/'):
            external_storage += '/'
        print(f'Partition values where disk_name is archive: {partitions}')
        worker_id = random.choice(self.workers_instance_id())
        if not worker_id:
            raise ValueError('Instance id not provided')

        print(f'Worker instance id: {worker_id}')
        # Create the database query
        # If org_id is '-1' we want to get all records with all cust ids
        # If we have actual cust id, then use it to restrict the result set.
        # Compression codec changed to 'gzip' for the parquet file for
        # external storage as default codec is 'LZ4' for the parquet file
        # generated by clickhouse
        org_clause = "" if org_id == -1 \
            else f"AND phCustId = {org_id}"
        query = f"""
              SELECT
                  phRecvTime,
                  phCustId,
                  customer,
                  eventType,
                  rawEventMsg
              FROM
                 fsiem.events_replicated
              WHERE
                  _partition_value IN ({partitions})
                  {org_clause}
              FORMAT {file_format}
              SETTINGS output_format_parquet_compression_method='gzip'
        """.replace('\n', '')

        full_file = f"{file_name}_file.{file_format}"
        print(f'File name: {full_file}')
        dest = f"aws s3 cp - s3://{external_storage}{full_file.lower()}"
        # *************************************************************
        # tee - monitor the progress of data through a pipe
        # Here 'ptee >(wc -c >&2)' is to get the total data transferred to
        # s3 bucket in bytes
        # To use it, insert it in a pipeline between two processes, with
        # the appropriate options.  Its standard input will be passed
        # through to its standard output and progress will be shown on
        # standard error
        # *************************************************************

        # Define the command parts
        # Note:- In the clickhouse query, '\\"' and not just '\"' is needed,
        # so that when shell script is executed by ssm command,
        # the select statement is seen within ""
        cmd = [
            'bash',
            '-c',
            f'"clickhouse-client --query \\"{query}\\" |',
            'tee >(wc -c >&2) |',
            f'{dest}"'
        ]

        # Join the command parts into a single string
        full_cmd_str = ' '.join(cmd)
        full_cmd = [full_cmd_str]

        # Long-running operation, pass in different value,
        # Check every minute for 24 hours looks like:
        waiter_config = {'Delay': 60, 'MaxAttempts': 1440}
        # As we only send this to one node, return the first result
        return self.ssm.exec_commands([worker_id], full_cmd, **waiter_config)

    def clickhouse_delete_partitions(self, partitions: list[str],
                                     db='fsiem', table='events_replicated'):
        """Schedules a delete of the specified partitions from a table. Delete
        will run in approx 10 minutes after being scheduled, see:
        https://clickhouse.com/docs/en/sql-reference/statements/alter/partition/#drop-partitionpart # noqa


         Parameters
        ----------
        partitions: list[str]
            List of partitions to be deleted from a table
        db: str
            Database name, defaults to fsiem
        table: str
            Table name, defaults to events_replicated
        """
        # Only allow chars from a strict white list
        validator.enforce_subset_ascii(db)
        validator.enforce_subset_ascii(table)
        validator.enforce_list_subset_ascii(partitions)

        worker_id = random.choice(self.workers_instance_id())
        if not worker_id:
            raise ValueError('Instance id not provided')

        print(f'Deleting {len(partitions)} partitions from the '
              'fsiem.events_replicated table. This query tags the partition '
              'as inactive and deletes data completely, approximately in '
              '10 minutes.')

        for p in partitions:
            print(f'Deleting partition: {p}')

            # Parametrized query
            # Note: '{ ... }' is literal, do not prefix this string with f
            sql = '''
                ALTER TABLE
                    {db:Identifier}.{tbl:Identifier}
                DROP PARTITION
                    ({p0:UInt32},{p1:UInt32})
                '''.replace('\n', '')

            chunks = self._split_partition_into_2_chunks(p)

            query = f'''
                clickhouse-client
                    --param_db="{db}"
                    --param_tbl="{table}"
                    --param_p0="{chunks[0]}"
                    --param_p1="{chunks[1]}"
                    --query="{sql}"
            '''.replace('\n', '')
            print(f'Executing clickhouse query on {worker_id}, query: {query}')
            try:
                resp = self.ssm.exec_command(worker_id, query)
                print(resp)
            except Exception as ex:
                print(f'Failed to on {query}, error: {ex}')

    def expand_workers_clickhouse_fs(self) -> list[SsmCmdResponse]:
        """Expand CH file system to use all available disk space on workers.

        When the file system already uses full disk, the command runs fine.
        If the file system can be expanded, it will be expanded. The operation
        runs on all workers in parallel and blocks until all are executed. In
        case of an error this will throw an exception. Disks are found by
        their mount point names (contains 'clickhouse'). For example,
        '/data-clickhouse-hot-1' will be expanded, but disk '/foo' will not.
        """
        ids = self.workers_instance_id()
        if not ids:
            raise ValueError('Instance id not provided')

        # Get mount points of all disks. Select only those with the word
        # 'clickhouse', e.g. /data-clickhouse-hot-1. Convert output to args,
        # feeding one argument at a time. Grow every mount point to max size.
        cmd = """
            df --output=target | grep clickhouse |
            xargs -n 1 sudo xfs_growfs -d
            """.replace('\n', '')
        return self.ssm.exec_commands(ids, [cmd])

    def clickhouse_backup_create(self, name: str,
                                 type: BackupType,
                                 previous_backup_name: str,
                                 options: dict,
                                 option_overrides: list[tuple] = None) \
            -> SsmCmdResponse:
        """Synchronously run full or incremental backup on a worker node

        Parameters
        ----------
        name : str
            Name of the backup
        type : BackupType
            Full or Incremental backup type
        previous_backup_name : str
            If incremental backup, this should be the name of the prev backup
        options: dict
            A dictionary with clickhouse-backup config options
        option_overrides: list[tuple]
            A list of key-value pairs used for any overrides and passing
            additional backup options

        Returns
        -------
        SsmCmdResponse
            Status of the command
        """
        # Safeguard against injection attack
        validator.enforce_subset_ascii(name)
        validator.enforce_subset_ascii(type.name)
        # Previous backup name can be None, when we run for the first time
        if previous_backup_name:
            validator.enforce_subset_ascii(previous_backup_name)
        validator.enforce_dict_subset_ascii(options)
        # We don't expect overrides, these can be None
        if option_overrides:
            for override in option_overrides:
                validator.enforce_list_subset_ascii(override)

        id = self.workers_instance_id()[0]
        if not id:
            raise ValueError('Instance id not provided')

        # Pass config via environmental variables
        cmd = [
            f'export REMOTE_STORAGE={options["remote_storage"]}',
            f'export LOG_LEVEL={options["log_level"]}',
            f'export S3_BUCKET={options["s3_bucket"]}',
            f'export S3_REGION={options["region"]}',
            f'export S3_PATH={options["s3_path"]}',
            f'export S3_COMPRESSION_LEVEL={options["s3_compression_level"]}',
            f'export S3_COMPRESSION_FORMAT={options["s3_compression_format"]}',
            f'export S3_USE_CUSTOM_STORAGE_CLASS={options["s3_use_custom_storage_class"]}',  # noqa
            f'export S3_STORAGE_CLASS={options["s3_storage_class"]}',
            f'export S3_CONCURRENCY={options["s3_concurrency"]}',
            f'export S3_DEBUG={options["s3_debug"]}'
        ]
        if option_overrides:
            print('Additional arguments received for clickhouse-backup')
            print(str(option_overrides))
            for key, value in option_overrides:
                cmd = cmd + [f'export {key}={value}']

        full_backup_cmd = [f'clickhouse-backup create_remote {name}']
        inc_backup_cmd = ['clickhouse-backup create_remote '
                          f'--diff-from-remote {previous_backup_name} '
                          f'{name}']
        if type == BackupType.FULL:
            cmd = cmd + full_backup_cmd
        elif type == BackupType.INCREMENTAL:
            cmd = cmd + inc_backup_cmd
        else:
            raise ValueError(f'Unsupported backup type: {type}')

        waiter_config = {'Delay': 10, 'MaxAttempts': 8640}
        # As we only send this to one node, return the first result
        return self.ssm.exec_commands([id], cmd, TIMEOUT_23_HOURS_IN_SECONDS,
                                      **waiter_config)[0]

    def clickhouse_backup_restore(self, name: str,
                                  options: dict) -> SsmCmdResponse:
        """Synchronously restore a full or incremental backup on a worker node

        Parameters
        ----------
        name : str
            Name of the backup
        options: kwargs
           A dictionary with clickhouse-backup config options

        Returns
        -------
        SsmCmdResponse
            Status of the command
        """
        # Safeguard against injection attack
        validator.enforce_subset_ascii(name)
        validator.enforce_dict_subset_ascii(options)

        id = self.workers_instance_id()[0]
        if not id:
            raise ValueError('Instance id not provided')

        # Pass config via environmental variables
        cmd = [
            f'export REMOTE_STORAGE={options["remote_storage"]}',
            f'export LOG_LEVEL={options["log_level"]}',
            f'export S3_BUCKET={options["s3_bucket"]}',
            f'export S3_REGION={options["region"]}',
            f'export S3_PATH={options["s3_path"]}',
            f'export S3_COMPRESSION_LEVEL={options["s3_compression_level"]}',
            f'export S3_COMPRESSION_FORMAT={options["s3_compression_format"]}',
            f'export S3_USE_CUSTOM_STORAGE_CLASS={options["s3_use_custom_storage_class"]}',  # noqa
            f'export S3_STORAGE_CLASS={options["s3_storage_class"]}',
            f'export S3_CONCURRENCY={options["s3_concurrency"]}',
            f'export S3_DEBUG={options["s3_debug"]}',
            f'clickhouse-backup restore_remote --drop {name}',
        ]
        waiter_config = {'Delay': 10, 'MaxAttempts': 8640}
        # As we only send this to one node, return the first result
        return self.ssm.exec_commands([id], cmd, TIMEOUT_23_HOURS_IN_SECONDS,
                                      **waiter_config)[0]

    def clickhouse_backup_delete(self, name: str, location: str,
                                 options: dict) -> SsmCmdResponse:
        """Synchronously delete local or remote backup

        Parameters
        ----------
        name : str
            Name of the backup
        location : str
            local or remote
        options: kwargs
           A dictionary with clickhouse-backup config options

        Returns
        -------
        SsmCmdResponse
            Status of the command
        """
        # Safeguard against injection attack
        validator.enforce_subset_ascii(name)
        validator.enforce_subset_ascii(location)
        validator.enforce_dict_subset_ascii(options)

        id = self.workers_instance_id()[0]
        if not id:
            raise ValueError('Instance id not provided')

        # Pass config via environmental variables
        cmd = [
            f'export REMOTE_STORAGE={options["remote_storage"]}',
            f'export LOG_LEVEL={options["log_level"]}',
            f'export S3_BUCKET={options["s3_bucket"]}',
            f'export S3_REGION={options["region"]}',
            f'export S3_PATH={options["s3_path"]}',
            f'export S3_DEBUG={options["s3_debug"]}',
            f'clickhouse-backup delete {location} {name}'
        ]
        waiter_config = {'Delay': 10, 'MaxAttempts': 8640}
        # As we only send this to one node, return the first result
        return self.ssm.exec_commands([id], cmd, TIMEOUT_1_HOUR_IN_SECONDS,
                                      **waiter_config)[0]

    def clickhouse_backup_list(self, options) -> list[BackupListItem]:
        """List existing backups, including local and remote

        Parameters
        ----------
        options: kwargs
           A dictionary with clickhouse-backup config options

        Returns
        -------
        list[BackupListItem]
            A list of backup items
        """
        # Safeguard against injection attack
        validator.enforce_dict_subset_ascii(options)

        id = self.workers_instance_id()[0]
        if not id:
            raise ValueError('Instance id not provided')

        # First pass config via environmental variables, then run a command
        cmd = [
            f'export REMOTE_STORAGE={options["remote_storage"]}',
            f'export LOG_LEVEL={options["log_level"]}',
            f'export S3_BUCKET={options["s3_bucket"]}',
            f'export S3_REGION={options["region"]}',
            f'export S3_PATH={options["s3_path"]}',
            'clickhouse-backup list all'
        ]
        # As we only send this to one node, return the first result
        resp = self.ssm.exec_commands([id], cmd)[0]
        lines = resp.output.splitlines()
        result = []
        for line in lines:
            if 'broken' in line:
                print(f'WARN: Skipping line as broken: {line}')
                continue

            try:
                result.append(BackupListItem.parse(line))
            except Exception as err:
                print(f'WARN: ignoring item {line}, err: {err}')
        return result

    def clickhouse_backup_cleanup(self, options) -> SsmCmdResponse:
        """Cleanup local backups

        Parameters
        ----------
        options: kwargs
           A dictionary with clickhouse-backup config options

        Returns
        -------
        SsmCmdResponse
            Status of the command
        """
        # Safeguard against injection attack
        validator.enforce_dict_subset_ascii(options)

        id = self.workers_instance_id()[0]
        if not id:
            raise ValueError('Instance id not provided')

        # First pass config via environmental variables, then run a command
        cmd = [
            f'export REMOTE_STORAGE={options["remote_storage"]}',
            f'export S3_BUCKET={options["s3_bucket"]}',
            f'export S3_REGION={options["region"]}',
            f'export S3_PATH={options["s3_path"]}',
            'clickhouse-backup clean',
            # TODO: investigate if this is needed, atm fails with access denied
            # 'clickhouse-backup clean_remote_broken',
        ]
        # As we only send this to one node, return the first result
        return self.ssm.exec_commands([id], cmd)[0]

    def clickhouse_metrics(self, instance_dns: str) -> SsmCmdResponse:
        """Get Clickhouse system metrics

        Returns
        -------
        SsmCmdResponse
            Status of the command
        """
        # Safeguard against injection attack
        validator.enforce_subset_ascii(instance_dns)
        id = self.worker_instance_id_by_dns(instance_dns)
        if not id:
            raise ValueError('Instance id not provided')

        sql = '''
            SELECT
                *
            FROM
                system.metrics
            WHERE
                metric in ({m1:String}, {m2:String})
            FORMAT JSON
                 '''.replace('\n', '')
        query = f'''
            clickhouse-client
                --param_m1="Query"
                --param_m2="Merge"
                --query="{sql}"
        '''.replace('\n', '')
        return self.ssm.exec_commands([id], [query])[0]

    def clickhouse_query_duration(self, instance_dns: str) -> SsmCmdResponse:
        """Get clickhouse query duration

        Returns
        -------
        SsmCmdResponse
            Status of the command
        """
        # Safeguard against injection attack
        validator.enforce_subset_ascii(instance_dns)

        id = self.worker_instance_id_by_dns(instance_dns)
        if not id:
            raise ValueError('Instance id not provided')

        sql = '''
            SELECT
                toStartOfHour(event_time) AS event_time_h,
                count() AS count_m,
                avg(query_duration_ms) AS avg_duration
            FROM
                clusterAllReplicas(fsiem_cluster, system.query_log)
            WHERE
                query_kind = {kind:String}
                    AND
                type != {type:String}
                    AND
                event_time > (now() - toIntervalDay(3))
            GROUP BY
                event_time_h
            ORDER BY
                event_time_h ASC
            FORMAT JSON
                '''.replace('\n', '')
        query = f'''
            clickhouse-client
                --param_kind="Select"
                --param_type="QueryStart"
                --query="{sql}"
        '''.replace('\n', '')
        return self.ssm.exec_commands([id], [query])[0]

    def clickhouse_query_count(self, instance_dns: str) -> SsmCmdResponse:
        """Get clickhouse query count by client

        Returns
        -------
        SsmCmdResponse
            Status of the command
        """
        # Safeguard against injection attack
        validator.enforce_subset_ascii(instance_dns)

        id = self.worker_instance_id_by_dns(instance_dns)
        if not id:
            raise ValueError('Instance id not provided')

        sql = '''
            SELECT
                toStartOfMinute(event_time) AS event_time_m,
                if(empty(client_name), 'unknown_or_http', client_name)
                    AS client_name,
                count(),
                query_kind
            FROM
                clusterAllReplicas(fsiem_cluster, system.query_log)
            WHERE
                type = {type:String}
                    AND
                event_time > (now() - toIntervalMinute(10))
                    AND
                query_kind = {kind:String}
            GROUP BY
                event_time_m,
                client_name,
                query_kind
            ORDER BY
                event_time_m DESC,
                count() ASC LIMIT 100
            FORMAT JSON
                '''.replace('\n', '')
        query = f'''
            clickhouse-client
                --param_kind="Select"
                --param_type="QueryStart"
                --query="{sql}"
        '''.replace('\n', '')
        return self.ssm.exec_commands([id], [query])[0]

    def clickhouse_online_parts(self) -> dict:
        """Get clickhouse online partition sizes

        Returns
        -------
        dict
            A json object
        """
        id = self.workers_instance_id()[0]
        if not id:
            raise ValueError('Instance id not found')

        results = []
        take = 50
        skip = 0
        sql = r'''
                SELECT
                    hostname() as host,
                    extract(partition, '\(\d+,(\d+)\)') as day,
                    sum(rows) as rows,
                    sum(bytes_on_disk) as bytes,
                    round(bytes / rows) as avgBytes,
                    sum(data_uncompressed_bytes) as uncompressedBytes,
                    round(uncompressedBytes / rows) as avgUncompressedBytes
                FROM
                    clusterAllReplicas(fsiem_cluster, system.parts)
                WHERE
                    table = 'events_replicated'
                    and active
                    and disk_name != 'archive'
                GROUP BY host, day
                ORDER BY day DESC
                LIMIT {take:UInt32}
                OFFSET {skip:UInt32}
                FORMAT JSON
                '''
        while True:
            query = f'''
                clickhouse-client
                    --param_take="{take}"
                    --param_skip="{skip}"
                    --query="{sql}"
            '''.replace('\n', '')
            resp = self.ssm.exec_command(id, query)
            output = json.loads(resp.output)

            if not output['data']:
                print('No more data')
                break
            skip += take

            print(f'Pulled {len(output["data"])} records...')
            for item in output['data']:

                # Shorten variables names for reducing data size
                results.append({
                    'd': item['day'],
                    'r': item['rows'],
                    'b': item['bytes'],
                    'aB': item['avgBytes'],
                    'uB': item['uncompressedBytes'],
                    'aUB': item['avgUncompressedBytes']
                })

        print(f'Finished getting metrics, returning {len(results)} records')
        return results

    def clickhouse_online_parts_gz(self) -> bytes:
        """Get clickhouse online partition sizes, then compress a JSON
        object with GZIP compressor, this is useful to minimize the size
        of the data we need to store in DynamoDB

        Returns
        -------
        bytes
            Compressed bytes of JSON partition sizes
        """
        parts = self.clickhouse_online_parts()
        parts_str = json.dumps(parts)
        compressor = GzipCompress()
        return compressor.compress_str(parts_str)

    def clickhouse_archive_parts(self) -> dict:
        """Get clickhouse archive partition sizes

        Returns
        -------
        dict
            A json object
        """
        id = self.workers_instance_id()[0]
        if not id:
            raise ValueError('Instance id not found')

        results = []
        take = 50
        skip = 0
        sql = r'''
            SELECT
                hostname() as host,
                extract(partition, '\(\d+,(\d+)\)') as day,
                sum(rows) as rows,
                sum(bytes_on_disk) as bytes,
                round(bytes / rows) as avgBytes,
                sum(data_uncompressed_bytes) as uncompressedBytes,
                round(uncompressedBytes / rows) as avgUncompressedBytes
            FROM
                clusterAllReplicas(fsiem_cluster, system.parts)
            WHERE
                table = 'events_replicated'
                and active
                and disk_name == 'archive'
            GROUP BY host, day
            ORDER BY day DESC
            LIMIT {take:UInt32}
            OFFSET {skip:UInt32}
            FORMAT JSON
            '''
        while True:

            query = f'''
                clickhouse-client
                    --param_take="{take}"
                    --param_skip="{skip}"
                    --query="{sql}"
            '''.replace('\n', '')
            resp = self.ssm.exec_command(id, query)
            output = json.loads(resp.output)

            if not output['data']:
                print('No more data')
                break
            skip += take

            print(f'Pulled {len(output["data"])} records...')
            for item in output['data']:

                # Shorten variables names for reducing data size
                results.append({
                    'd': item['day'],
                    'r': item['rows'],
                    'b': item['bytes'],
                    'aB': item['avgBytes'],
                    'uB': item['uncompressedBytes'],
                    'aUB': item['avgUncompressedBytes']
                })

        print(f'Finished getting metrics, returning {len(results)} records')
        return results

    def clickhouse_archive_parts_gz(self) -> bytes:
        """Get clickhouse archive partition sizes, then compress a JSON
        object with GZIP compressor, this is useful to minimize the size
        of the data we need to store in DynamoDB

        Returns
        -------
        bytes
            Compressed bytes of JSON partition sizes
        """
        parts = self.clickhouse_archive_parts()
        parts_str = json.dumps(parts)
        compressor = GzipCompress()
        return compressor.compress_str(parts_str)

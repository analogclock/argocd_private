import csv
from calc import STORAGE_TYPE, FsiemResourceScale, LAST_CHANGED_ON, VERSION


class CsvDataProvider:

    def __init__(self, csv_file_name: str, storage_type: STORAGE_TYPE) -> None:
        self.csv_file_name = csv_file_name
        self.storage_type = storage_type

    def _read_clickhouse(self):
        with open(self.csv_file_name, mode='r') as f:
            reader = csv.reader(f)
            # Expect 1 header line in the csv, skip first line
            next(reader, None)
            for line in reader:
                result = FsiemResourceScale(
                    shards=1,
                    replicas=2,
                    data_workers=2,
                    keeper_workers=int(line[8]),
                    ingestion_workers=int(line[10]),
                    super_instance_types=[line[1].lower()],
                    worker_instance_types=[line[4].lower()],
                    keeper_instance_types=[line[7].lower()],
                    ingestion_instance_types=[line[9].lower()],
                    cmdb_iops=int(line[2]),
                    cmdb_throughput=int(line[3]),
                    opt_iops=int(line[2]),
                    opt_throughput=int(line[3]),
                    data_disk_throughput=int(line[5]),
                    data_disk_iops=int(line[6]),
                    data_disk_count=5,
                    data_disk_size=100,
                    app_server_mem_gb=0,
                    number_of_seats=int(line[0]),
                    last_changed_on=LAST_CHANGED_ON,
                    version=VERSION)
                yield result

    def _read_eventdb(self):
        with open(self.csv_file_name, mode='r') as f:
            reader = csv.reader(f)
            # Expect two header lines in the csv, skip 2 first lines
            next(reader, None)
            next(reader, None)
            for line in reader:
                result = FsiemResourceScale(
                    shards=0,
                    replicas=0,
                    data_workers=int(line[13].replace('*', '')),
                    keeper_workers=0,
                    ingestion_workers=0,
                    super_instance_types=[],
                    worker_instance_types=[],
                    keeper_instance_types=[],
                    ingestion_instance_types=[],
                    cmdb_iops=int(line[10].replace('K', '000')),
                    cmdb_throughput=int(line[11]),
                    opt_iops=int(line[10].replace('K', '000')),
                    opt_throughput=int(line[11]),
                    data_disk_throughput=int(line[16].replace('*', '')),
                    data_disk_count=5,
                    data_disk_iops=3000,
                    data_disk_size=100,
                    app_server_mem_gb=int(line[12]),
                    number_of_seats=int(line[2]),
                    last_changed_on=LAST_CHANGED_ON,
                    version=VERSION)
                yield result

    def read(self):
        if self.storage_type == STORAGE_TYPE.CLICKHOUSE:
            return self._read_clickhouse()
        if self.storage_type == STORAGE_TYPE.EVENTDB:
            return self._read_eventdb()
        raise ValueError(f'Unexpected value: {self.storage_type}')

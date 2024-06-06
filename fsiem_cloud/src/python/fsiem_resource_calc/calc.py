from dataclasses import dataclass
from enum import Enum


# For dev use, manually update when something is changed in the calculator
LAST_CHANGED_ON: str = '2024-01-18'  # YYYY-MM-DD
VERSION: str = '1.0.8'

# v1.0.8 (2024-01-18)
# - Added ingestion_workers and ingestion_instance_types


class STORAGE_TYPE(Enum):
    CLICKHOUSE = 'clickhouse'
    EVENTDB = 'eventdb'


class EC2_INSTANCE_SET:
    # NB: older instances may have unexpected scaling,
    # e.g. c5.9xlarge
    m_xlarge = ['m6i.xlarge', 'm6a.xlarge', 'm5.xlarge']
    m_2xlarge = ['m6i.2xlarge', 'm6a.2xlarge', 'm5.2xlarge']
    m_4xlarge = ['m6i.4xlarge', 'm6a.4xlarge', 'm5.4xlarge']
    m_8xlarge = ['m6i.8xlarge', 'm6a.8xlarge', 'm5.8xlarge']
    m_16xlarge = ['m6i.16xlarge', 'm6a.16xlarge', 'm5.16xlarge']

    c_xlarge = ['c6i.xlarge', 'c6a.xlarge', 'c5.xlarge']
    c_2xlarge = ['c6i.2xlarge', 'c6a.2xlarge', 'c5.2xlarge']
    c_4xlarge = ['c6i.4xlarge', 'c6a.4xlarge', 'c5.4xlarge']
    c_8xlarge = ['c6i.8xlarge', 'c6a.8xlarge', 'c5.9xlarge']
    c_16xlarge = ['c6i.16xlarge', 'c6a.16xlarge', 'c5.18xlarge']

    # only used for compute level 1
    r_large = ['r6i.large', 'r6a.large', 'r5.large']


@dataclass
class FsiemResourceScale:
    """Required resources for FSIEM cloud deployment"""
    shards: int
    replicas: int
    data_workers: int
    keeper_workers: int
    ingestion_workers: int
    super_instance_types: list
    worker_instance_types: list
    keeper_instance_types: list
    ingestion_instance_types: list
    cmdb_iops: int
    cmdb_throughput: int
    data_disk_iops: int
    data_disk_throughput: int
    opt_iops: int
    opt_throughput: int
    data_disk_count: int
    data_disk_size: int
    app_server_mem_gb: int
    number_of_seats: int
    last_changed_on: str
    version: str


class Calc:
    """Parent class for calculating resources for FSIEM deployment"""

    def __init__(self, number_of_seats: int, online_size: int = 500,
                 max_per_disk: int = 10000) -> None:
        self.n = number_of_seats
        self.online_size = online_size
        self.max_per_disk = max_per_disk

    def get_app_server_mem_gb(self) -> int:
        """Get app server memory in GB"""
        if self.n >= 1 and self.n <= 6:
            return 5
        if self.n > 6 and self.n <= 14:
            return 10
        if self.n > 14 and self.n <= 1000:
            return 20
        raise ValueError(f'Number of seats is out of bounds for {self.n}')

    # pass - means this method is expected to be implemented by a child class
    # Do nothing in the parent class. This is still needed to be here,
    # as get_common uses this methods and expects child classes to return
    # different values. E.g. we expect different number of worker nodes
    # for ClickHouse deployment vs EventDb
    def get_data_workers(self) -> int:
        pass

    def get_keeper_workers(self) -> int:
        pass

    def get_ingestion_workers(self) -> int:
        pass

    def get_super_instance_types(self) -> list:
        pass

    def get_worker_instance_types(self) -> list:
        pass

    def get_keeper_instance_types(self) -> list:
        pass

    def get_ingestion_instance_types(self) -> list:
        pass

    def get_cmdb_iops(self) -> int:
        pass

    def get_cmdb_throughput(self) -> int:
        pass

    def get_data_disk_iops(self) -> int:
        pass

    def get_data_disk_throughput(self) -> int:
        pass

    def get_opt_iops(self) -> int:
        pass

    def get_opt_throughput(self) -> int:
        pass

    def get_data_disk_count(self) -> int:
        """Get the number of disks used for storing data"""
        return 5

    def get_data_disk_size(self) -> int:
        """Get the size of each disk used for storing data"""
        return min(self.online_size // self.get_data_disk_count(),
                   self.max_per_disk)

    def get(self) -> FsiemResourceScale:
        pass

    def get_common(self, replicas, shards) -> FsiemResourceScale:
        """Calculate needed resources"""
        # Calculate number of data workers, logic prepped by DH
        data_workers = self.get_data_workers()

        # Number of dedicated keeper worker nodes
        keepers = self.get_keeper_workers()

        # Number of ingestion workers
        ingestion_workers = self.get_ingestion_workers()

        # what kind of EC2 instances to use
        super_types = self.get_super_instance_types()
        worker_types = self.get_worker_instance_types()
        keeper_types = self.get_keeper_instance_types()
        ingestion_types = self.get_ingestion_instance_types()

        cmdb_iops = self.get_cmdb_iops()
        cmdb_throughput = self.get_cmdb_throughput()

        data_disk_iops = self.get_data_disk_iops()
        data_disk_throughput = self.get_data_disk_throughput()
        data_disk_count = self.get_data_disk_count()
        data_disk_size = self.get_data_disk_size()

        opt_iops = self.get_opt_iops()
        opt_throughput = self.get_opt_throughput()

        app_server_mem_gb = self.get_app_server_mem_gb()

        return FsiemResourceScale(
            shards=shards, replicas=replicas, data_workers=data_workers,
            keeper_workers=keepers, ingestion_workers=ingestion_workers,
            super_instance_types=super_types,
            worker_instance_types=worker_types,
            keeper_instance_types=keeper_types,
            ingestion_instance_types=ingestion_types, cmdb_iops=cmdb_iops,
            cmdb_throughput=cmdb_throughput,
            data_disk_iops=data_disk_iops,
            data_disk_throughput=data_disk_throughput,
            data_disk_count=data_disk_count,
            data_disk_size=data_disk_size,
            opt_iops=opt_iops,
            opt_throughput=opt_throughput,
            app_server_mem_gb=app_server_mem_gb,
            number_of_seats=self.n,
            last_changed_on=LAST_CHANGED_ON,
            version=VERSION)

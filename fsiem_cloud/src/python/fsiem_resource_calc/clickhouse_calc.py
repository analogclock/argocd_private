from calc import EC2_INSTANCE_SET, Calc, FsiemResourceScale


class ClickHouseCalc(Calc):
    """Class for calculating required resources for ClickHouse deployment"""

    def __init__(self, number_of_seats: int, online_size: int,
                 max_per_disk: int = 10000) -> None:
        self._validate_number_of_seats(number_of_seats)
        if online_size < 0:
            raise ValueError(f'Online size cannot be negative: {online_size}')
        if max_per_disk < 0:
            raise ValueError(f'Max size cannot be negative: {max_per_disk}')
        super().__init__(number_of_seats, online_size, max_per_disk)

    def _validate_number_of_seats(self, n: int):
        """Number of seats can be within the range [1 .. 1000]

        Parameters
        ----------
        n : int
            Number of seats, range [1 .. 1000]
        """
        if n < 1 or n > 1000:
            raise ValueError(f'Number of seats is out of bounds: {n}. ' +
                             'Valid range for Clickhouse is [1..1000] seats.')

    def get_data_workers(self) -> int:
        """Get number of workers based on Scalability Test v1 spreadsheet.

        Even though license can only be purchased with this increments:
        From [5 .. 30] seat change increment 1
            You cannot get 31, 32..34
        From [35 .. 175] seat change increment 5
            You cannot get 176, 177, .. 199
        From [200 .. 1000] seat change increment 50

        We assume, it could be possible to combine several entitlements.

        For example:
            n = 59, we return a tier (60 seats), so 2 nodes
            n = 60, we return a tier (60 seats), so 2 nodes
            n = 61, we return a next tier (65 seats), so 2 nodes
        """
        if self.n <= 60:
            return 2

        # although currently we do equal increments of 60 now
        # I don't want to remove this in case it changes in future
        # we assume 1 worker can handle 30K, and we always double the workers
        if self.n > 60 and self.n <= 120:
            return 4
        if self.n > 120 and self.n <= 180:
            return 6
        if self.n > 180 and self.n <= 240:
            return 8
        if self.n > 240 and self.n <= 300:
            return 10
        if self.n > 300 and self.n <= 360:
            return 12
        if self.n > 360 and self.n <= 420:
            return 14
        if self.n > 420 and self.n <= 480:
            return 16
        if self.n > 480 and self.n <= 540:
            return 18
        if self.n > 540 and self.n <= 600:
            return 20
        if self.n > 600 and self.n <= 660:
            return 22
        if self.n > 660 and self.n <= 720:
            return 24
        if self.n > 720 and self.n <= 780:
            return 26
        if self.n > 780 and self.n <= 840:
            return 28
        if self.n > 840 and self.n <= 900:
            return 30
        if self.n > 900 and self.n <= 960:
            return 32
        if self.n > 960 and self.n <= 1000:
            return 34
        raise ValueError(f'Number of seats is out of bounds for {self.n}')

    def get_keeper_workers(self) -> int:
        """Get number of worker keeper nodes
        [1 .. 2]   - 0, no dedicated keeper worker
        [3 .. 60]   - 1, one dedicated keeper worker
        [61 .. 100]  - 3, three dedicated keeper workers
        """
        if self.n == 1 or self.n == 2:
            return 0
        if self.n > 2 and self.n <= 60:
            return 1
        else:
            return 3

    def get_ingestion_workers(self) -> int:
        """Get number of ingestion workers. Currently fixed at 0
        """
        return 0

    def get_super_instance_types(self) -> list:
        """Get AWS EC2 instance sets for super deployment"""
        if self.n == 1:
            return EC2_INSTANCE_SET.r_large
        if self.n > 1 and self.n <= 4:
            return EC2_INSTANCE_SET.m_2xlarge
        if self.n > 4 and self.n <= 8:
            return EC2_INSTANCE_SET.m_2xlarge
        if self.n > 8 and self.n <= 25:
            return EC2_INSTANCE_SET.m_4xlarge
        if self.n > 25 and self.n <= 60:
            return EC2_INSTANCE_SET.m_8xlarge
        if self.n > 60 and self.n <= 1000:
            return EC2_INSTANCE_SET.m_16xlarge
        raise ValueError(f'Number of seats is out of bounds for {self.n}')

    def get_worker_instance_types(self) -> list:
        """Get AWS EC2 instance sets for data worker deployment"""
        if self.n == 1:
            return EC2_INSTANCE_SET.r_large
        if self.n > 1 and self.n <= 3:
            return EC2_INSTANCE_SET.m_xlarge
        if self.n > 3 and self.n <= 10:
            return EC2_INSTANCE_SET.m_2xlarge
        if self.n > 10 and self.n <= 20:
            return EC2_INSTANCE_SET.m_4xlarge
        if self.n > 20 and self.n <= 29:
            return EC2_INSTANCE_SET.m_8xlarge
        if self.n > 29 and self.n <= 1000:
            return EC2_INSTANCE_SET.m_16xlarge

    def get_keeper_instance_types(self) -> list:
        """Get AWS EC2 instance sets for worker keeper deployment"""
        if self.n == 1 or self.n == 2:
            return []
        if self.n > 2 and self.n <= 6:
            return EC2_INSTANCE_SET.c_xlarge
        if self.n > 6 and self.n <= 11:
            return EC2_INSTANCE_SET.c_2xlarge
        if self.n > 11 and self.n <= 1000:
            return EC2_INSTANCE_SET.c_4xlarge

    def get_ingestion_instance_types(self) -> list:
        """Get AWS EC2 instance sets for ingestion worker deployment"""
        return EC2_INSTANCE_SET.c_xlarge

    def get_cmdb_iops(self) -> int:
        """Get CMDB IOPS metric, this is one of the super disks"""
        if self.n >= 46:
            return 4000
        return 3000

    def get_cmdb_throughput(self) -> int:
        """Get CMDB throughput metric, this is one of the super disks"""
        if self.n >= 1 and self.n < 35:
            return 200
        if self.n >= 35 and self.n < 50:
            return 200 + (self.n - 34) * 50
        if self.n >= 50 and self.n <= 1000:
            return 1000

    def get_opt_iops(self) -> int:
        """Get OPT IOPS metric, this is one of the super/worker disks"""
        if self.n >= 46:
            return 4000
        return 3000

    def get_opt_throughput(self) -> int:
        """Get OPT throughput metric, this is one of the super/worker disks"""
        if self.n >= 1 and self.n < 35:
            return 200
        if self.n >= 35 and self.n < 50:
            return 200 + (self.n - 34) * 50
        if self.n >= 50 and self.n <= 1000:
            return 1000

    def get_data_disk_iops(self) -> int:
        # forced to 3000 iops on each disk
        return 3000

    def get_data_disk_throughput(self) -> int:
        """Get data disk throughput"""
        # gp3 throughput: [200 .. 1000], step 8
        # Seats 1: 200
        # Seats 2: 200 + (2 - 1) * 20 = 225
        # Seats 3: 200 + (3 - 1) * 20 = 245
        # Seats 60: 200 + (60 - 1) * 20 = 500 MAX
        return min(200 + (self.n - 1) * 20, 500)

    def get(self) -> FsiemResourceScale:
        """Calculate needed resources for ClickHouse

        Returns
        -------
        FsiemResourceScale
            FSIEM cloud resources needed based on the number of seats
        """
        data_workers = self.get_data_workers()
        shards = int(data_workers / 2)
        return super().get_common(replicas=2, shards=shards)

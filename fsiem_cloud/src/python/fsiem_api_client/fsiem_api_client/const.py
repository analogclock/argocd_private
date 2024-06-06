from enum import Enum

# PhMonitor takes time to restart, we allow 2 minutes for this
phmonitor_delay_sec = 120

# we need to wait for 7 minutes for all CH changes to propagate
ch_propagate_delay = 420


class FsiemInstanceRole(Enum):
    super = 'super'
    worker = 'worker'
    keeper = 'keeper'
    ingestion = 'ingestion'


# Known sizes of the disks we use for super/worker/keeper
# This is used when we enumerate all disks and exclude these known disks
# to find spare disks we can use for data (ClickHouse)
super_disk_sizes = ['25G', '60G', '100G', '80G']
worker_disk_sizes = ['25G', '100G']
keeper_disk_sizes = ['25G', '100G']


class BackupType(str, Enum):
    FULL = 'full'
    INCREMENTAL = 'incremental'


class BackupListItem:
    def __init__(self, name, human_size, created_on, location):
        self.name = name
        self.human_size = human_size
        self.created_on = created_on
        self.location = location

    @classmethod
    def parse(cls, line: str):
        items = line.split()
        # date and time joined by space
        dt = items[2] + ' ' + items[3]
        return cls(items[0], items[1], dt, items[4])

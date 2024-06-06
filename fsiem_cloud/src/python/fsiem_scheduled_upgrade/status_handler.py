from sched_upgrades_table import SchedUpgradesTable
from fsiem_api_client import ActivationTable


class StatusHandler:
    def __init__(self, serial_no: str, upgrade_path: str,
                 sched_table: SchedUpgradesTable,
                 activation_table: ActivationTable) -> None:
        self.serial_no = serial_no
        self.upgrade_path = upgrade_path
        self.sched_table = sched_table
        self.activation_table = activation_table

    def failure(self):
        """Handler for failed upgrade
        """
        print(f'Running failure handler for {self.serial_no}')
        self.sched_table.update_status(
            self.serial_no, self.upgrade_path,
            self.sched_table.status_failed, update_end_time=True
        )

    def success(self):
        """Handler for successful upgrade
        """
        print(f'Running success handler for {self.serial_no}')
        self.sched_table.update_status(
            self.serial_no, self.upgrade_path,
            self.sched_table.status_complete, update_end_time=True
        )

    def in_progress(self):
        """Handler for starting upgrade
        """
        print(f'Running in progress handler for {self.serial_no}')
        self.sched_table.update_status(
            self.serial_no, self.upgrade_path,
            self.sched_table.status_in_progress, update_start_time=True
        )

        self.activation_table.update_status(
            self.serial_no, self.activation_table.initializing
        )

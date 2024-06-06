import agent_util
import subprocess
from os import listdir
from os.path import join, isdir


# Template taken from:
# https://confluence-panopta.atlassian.net/wiki/spaces/PD/pages/718831637/template.py+file
class FsiemPlugin(agent_util.Plugin):
    textkey = "fsiem"
    label = "FortiSiem"

    @classmethod
    def get_metadata(self, config):
        status = agent_util.SUPPORTED
        msg = None
        metadata = {
            "license_valid": {
                "label": "License Valid",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "boolean"
            },
            "organization_count": {
                "label": "Organization Count",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "cmdb_user_count": {
                "label": "CMDB User Count",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "fsm_user_count": {
                "label": "FSM User Count",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "managed_device_count": {
                "label": "Managed Device Count",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "unmanaged_device_count": {
                "label": "Unmanaged Device Count",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "active_rule_count": {
                "label": "Active Rule Count",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "inactive_rule_count": {
                "label": "Inactive Rule Count",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "users": {
                "label": "Users",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "sessions": {
                "label": "Sessions",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "users_scheduled_reports": {
                "label": "User Scheduled Reports",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "dashboard_scheduled_reports": {
                "label": "Dashboard Scheduled Reports",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "malware_domain": {
                "label": "Malware Domain",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "malware_ip": {
                "label": " Malware IP",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "malware_url": {
                "label": "Malware URL",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "malware_process": {
                "label": "Malware Process",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "malware_hash": {
                "label": "Malware Hash",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "total_collectors": {
                "label": "Total Collectors",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "eps_3m": {
                "label": "Events/Second average 3 min",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "eps_15m": {
                "label": "Events/Second average 15 min",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "eps_30m": {
                "label": "Events/Second average 30 min",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "inline_report_queue_original": {
                "label": "Inline report queue original",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "inline_report_queue_i300": {
                "label": "Inline report queue i300",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "count"
            },
            "inline_report_queue_i900": {
                "label": "Inline report queue i900",
                "options": None,
                "status": status,
                "error_message": msg,
                "unit": "count"
            }
        }
        return metadata

    def check(self, textkey, data, config):
        if textkey == 'license_valid':
            return self.license_valid()
        if textkey == 'organization_count':
            return self.organization_count()
        if textkey == 'cmdb_user_count':
            return self.cmdb_user_count()
        if textkey == 'fsm_user_count':
            return self.fsm_user_count()
        if textkey == 'managed_device_count':
            return self.managed_device_count()
        if textkey == 'unmanaged_device_count':
            return self.unmanaged_device_count()
        if textkey == 'active_rule_count':
            return self.active_rule_count()
        if textkey == 'inactive_rule_count':
            return self.inactive_rule_count()
        if textkey == 'users':
            return self.users()
        if textkey == 'sessions':
            return self.sessions()
        if textkey == 'users_scheduled_reports':
            return self.users_scheduled_reports()
        if textkey == 'dashboard_scheduled_reports':
            return self.dashboard_scheduled_reports()
        if textkey == 'malware_domain':
            return self.malware_domain()
        if textkey == 'malware_ip':
            return self.malware_ip()
        if textkey == 'malware_url':
            return self.malware_url()
        if textkey == 'malware_process':
            return self.malware_process()
        if textkey == 'malware_hash':
            return self.malware_hash()
        if textkey == 'total_collectors':
            return self.total_collectors()
        if textkey.startswith('eps'):
            if textkey == 'eps_3m':
                return self.eps('3 Min')
            if textkey == 'eps_15m':
                return self.eps('15 Min')
            if textkey == 'eps_30m':
                return self.eps('30 Min')
            return None
        if textkey.startswith('inline_report_queue_'):
            if textkey == 'inline_report_queue_original':
                return self.original_inline_report_queue()
            if textkey == 'inline_report_queue_i300':
                return self.i_inline_report_queue('i300')
            if textkey == 'inline_report_queue_i900':
                return self.i_inline_report_queue('i900')

    def get_bool_count(self, bool_tbl):
        '''
                label     | xxxxxxxxxx | count
            ---------------+------------+-------
            ##BoolCount## | t          |     3
            ##BoolCount## | f          |     1
            ##BoolCount## |            |     1
        '''
        count_true = 0
        count_false = 0
        for line in bool_tbl.split('\n'):
            tokens = line.split('|')
            if tokens[0].find('##BoolCount##') < 0:
                continue
            is_true = tokens[1].strip()
            count = int(tokens[2].strip())
            if is_true == 't':
                count_true += count
            elif is_true == 'f' or is_true == '':
                count_false += count

        return (count_true, count_false)

    def license_valid(self):
        try:
            subprocess.check_call(
                ['/opt/phoenix/bin/phLicenseTool', '--verify']
            )
            return 1
        except subprocess.CalledProcessError:
            self.log.info(
                '/opt/phoenix/bin/phLicenseTool returned invalid return code'
            )
            return None
        except Exception as e:
            self.log.error(
                'Unexpected error when running /opt/phoenix/bin/phLicenseTool'
            )
            self.log.error(e)
            return None

    def organization_count(self):
        organization_count = None
        org_count_cmd = '''psql phoenixdb phoenix -c "select domain_id, name \
                           from ph_sys_domain where name<>'system' and \
                           name<>'service' and name<>'Super'" | \
                           tail -n +3 | head -n -2 | wc -l'''

        try:
            # Run the Bash command using subprocess
            result = subprocess.run(org_count_cmd, shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    universal_newlines=True)

            # Check if the command was successful
            if result.returncode == 0:
                organization_count = int(result.stdout.strip())
            else:
                # Print the error message if the command failed
                print(f"Error executing command: {result.stderr.strip()}")

        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")

        return organization_count

    def user_cmd(self):
        count_sys_admin = 0
        count_no_sys_admin = 0
        user_cmd = '''psql phoenixdb phoenix -c "select '##BoolCount##' \
                      as label, privileged, count(*) from ph_user where \
                      cust_org_id != 2 and cust_org_id != 0 and \
                      (for_agent = false or for_agent is null) \
                      group by privileged;"'''
        try:
            # Run the Bash command using subprocess
            result = subprocess.run(user_cmd, shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    universal_newlines=True)

            # Check if the command was successful
            if result.returncode == 0:
                count_sys_admin, count_no_sys_admin = \
                           self.get_bool_count(result.stdout)
            else:
                # Print the error message if the command failed
                print(f"Error executing command: {result.stderr.strip()}")

        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")

        return count_sys_admin, count_no_sys_admin

    def cmdb_user_count(self):
        cmdb_user_count = 0
        # Discard first value
        _, cmdb_user_count = self.user_cmd()
        return cmdb_user_count

    def fsm_user_count(self):
        fsm_user_count = 0
        # Discard second value
        fsm_user_count, _ = self.user_cmd()
        return fsm_user_count

    def device_cmd(self):
        count_unmanaged = 0
        count_managed = 0
        device_cmd = '''psql phoenixdb phoenix -c "select '##BoolCount##' as \
                        label,unmanaged,count(*) from ph_device \
                        group by unmanaged;"'''
        try:
            # Run the Bash command using subprocess
            result = subprocess.run(device_cmd, shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    universal_newlines=True)

            # Check if the command was successful
            if result.returncode == 0:
                count_unmanaged, count_managed = \
                           self.get_bool_count(result.stdout)
            else:
                # Print the error message if the command failed
                print(f"Error executing command: {result.stderr.strip()}")

        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")

        return count_unmanaged, count_managed

    def managed_device_count(self):
        managed_device_count = 0
        # Discard first value
        _, managed_device_count = self.device_cmd()
        return managed_device_count

    def unmanaged_device_count(self):
        unmanaged_device_count = 0
        # Discard second value
        unmanaged_device_count, _ = self.device_cmd()
        return unmanaged_device_count

    def rule_cmd(self):
        count_active = 0
        count_inactive = 0
        rule_cmd = '''psql phoenixdb phoenix -c "select '##BoolCount##' as \
                        label,active,count(*) from ph_drq_rule \
                        group by active;"'''
        try:
            # Run the Bash command using subprocess
            result = subprocess.run(rule_cmd, shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    universal_newlines=True)

            # Check if the command was successful
            if result.returncode == 0:
                count_active, count_inactive = \
                           self.get_bool_count(result.stdout)
            else:
                # Print the error message if the command failed
                print(f"Error executing command: {result.stderr.strip()}")

        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")

        return count_active, count_inactive

    def active_rule_count(self):
        active_rule_count = 0
        # Discard second value
        active_rule_count, _ = self.rule_cmd()
        return active_rule_count

    def inactive_rule_count(self):
        inactive_rule_count = 0
        # Discard first value
        _, inactive_rule_count = self.rule_cmd()
        return inactive_rule_count

    def parse_logon_user_info(self, usr_tbl):
        '''     label    | count |     label      | count
        -------------+-------+----------------+-------
         LogonUsers: |     1 | TotalSessions: |     2
        '''
        for line in usr_tbl.split('\n'):
            if not line:
                continue
            if "LogonUsers:" in line and "TotalSessions:" in line:
                _, users_str, _, sessions_str = \
                       map(str.strip, line.split("|", maxsplit=3))
                users = int(users_str)
                sessions = int(sessions_str)

        return users, sessions

    def logon_cmd(self):
        count_users = 0
        count_sessions = 0
        logon_cmd = '''psql phoenixdb phoenix -c "select 'LogonUsers:' as \
                      label, count(distinct(login_id)), 'TotalSessions:' as \
                      label, count(*) from ph_sec_ident; "'''
        try:
            # Run the Bash command using subprocess
            result = subprocess.run(logon_cmd, shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    universal_newlines=True)

            # Check if the command was successful
            if result.returncode == 0:
                count_users, count_sessions = \
                      self.parse_logon_user_info(result.stdout)
            else:
                # Print the error message if the command failed
                print(f"Error executing command: {result.stderr.strip()}")

        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")

        return count_users, count_sessions

    def users(self):
        count_users = 0
        # Discard second value
        count_users, _ = self.logon_cmd()
        return count_users

    def sessions(self):
        count_sessions = 0
        # Discard first value
        _, count_sessions = self.logon_cmd()
        return count_sessions

    def parse_report_count(report_tbl):
        ''' dashboardReport |     0
            userReport |     0
        '''
        scheduledDashboardReport = 0
        scheduledUserReport = 0
        for line in report_tbl.split('\n'):
            if "dashboardReport " in line:
                scheduledDashboardReport += int(line.rsplit(maxsplit=1)[-1])
            if "userReport " in line:
                scheduledUserReport += int(line.rsplit(maxsplit=1)[-1])

        return scheduledDashboardReport, scheduledUserReport

    def sch_reports_cmd(self):
        scheduledDashboardReport = 0
        scheduledUserReport = 0
        sch_reports_cmd = '''psql phoenixdb phoenix -f <(echo "select \
            'dashboardReport' as label, count(*) from ph_schedule \
            where (job_data_type = 'CmdbReport' or \
            job_data_type = 'AuditReport') AND job_data_id in \
            (select data_provider_id from ph_dbd_widget); \
            select 'userReport' as label, count(*) from ph_schedule \
            where (job_data_type = 'CmdbReport' \
            or job_data_type = 'AuditReport') AND \
            job_data_id not in (select data_provider_id from ph_dbd_widget) \
            ") | grep -F Report'''
        try:
            # Run the Bash command using subprocess
            result = subprocess.run(sch_reports_cmd, shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    universal_newlines=True)

            # Check if the command was successful
            if result.returncode == 0:
                scheduledDashboardReport, scheduledUserReport = \
                      self.parse_report_count(result.stdout)
            else:
                # Print the error message if the command failed
                print(f"Error executing command: {result.stderr.strip()}")

        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")

        return scheduledDashboardReport, scheduledUserReport

    def dashboard_scheduled_reports(self):
        dashboard_scheduled_reports = 0
        # Discard second value
        dashboard_scheduled_reports, _ = self.sch_reports_cmd()
        return dashboard_scheduled_reports

    def users_scheduled_reports(self):
        users_scheduled_reports = 0
        # Discard first value
        _, users_scheduled_reports = self.sch_reports_cmd()
        return users_scheduled_reports

    def get_malware_count(self, malware_name):
        result = {}

        for name, table_name in {
            'Malware Domain:':  'ph_malware_site',
            'Malware IP:':      'ph_malware_ip',
            'Malware URL:':     'ph_malware_url',
            'Malware Process:': 'ph_malware_proc',
            'Malware Hash:':    'ph_malware_hash',
        }.items():
            try:
                malware_cmd = f'''psql phoenixdb phoenix -c "select count(*) \
                             from {table_name};" | head -3 | tail -1'''

                # Run the Bash command using subprocess
                result_str = subprocess.run(malware_cmd, shell=True,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            universal_newlines=True
                                            ).stdout.strip()

                # Parse the count from the output
                count = int(result_str) if result_str.isdigit() else 0

                # Add count to the result dictionary
                if malware_name == name:
                    result[name] = count
            except subprocess.CalledProcessError as e:
                print(f"Error executing command: {e}")
                # Set count to 0 in case of error
                result[name] = 0

        return result

    def malware_domain(self):
        result = self.get_malware_count('Malware Domain:')
        # Convert to integer and handle None case
        return int(result.get('Malware Domain:', 0))

    def malware_ip(self):
        result = self.get_malware_count('Malware IP:')
        return int(result.get('Malware IP:', 0))

    def malware_url(self):
        result = self.get_malware_count('Malware URL:')
        return int(result.get('Malware URL:', 0))

    def malware_process(self):
        result = self.get_malware_count('Malware Process:')
        return int(result.get('Malware Process:', 0))

    def malware_hash(self):
        result = self.get_malware_count('Malware Hash:')
        return int(result.get('Malware Hash:', 0))

    def get_collectors(self, collectors_data):
        '''
                label       | name  | count
            -------------------+-------+-------
            ##COLLECOTRDATA## | Super |     1
        '''
        total = 0
        for line in collectors_data.split('\n'):
            tokens = line.split('|')
            if tokens[0].find('##COLLECOTRDATA##') < 0:
                continue
            count = int(tokens[2].strip())
            total += count

        return total

    def collector_counts_cmd(self):
        collectors_data = 0
        collector_counts_cmd = '''psql phoenixdb phoenix -c \
                                  "select '##COLLECOTRDATA##' as label, \
                                  t2.name, count(*) from ph_sys_collector t1 \
                                  inner join ph_sys_domain t2 on \
                                  t1.cust_org_id = t2.domain_id group \
                                  by t2.name;"'''
        try:
            # Run the Bash command using subprocess
            result = subprocess.run(collector_counts_cmd, shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    universal_newlines=True)

            # Check if the command was successful
            if result.returncode == 0:
                collectors_data = self.get_collectors(result.stdout)
            else:
                # Print the error message if the command failed
                print(f"Error executing command: {result.stderr.strip()}")

        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")

        return collectors_data

    def total_collectors(self):
        return self.collector_counts_cmd()

    def eps(self, avg_time):
        eps_file = '/tmp/EventPerSecInfo'
        try:
            with open(eps_file, 'r') as f:
                # 3 Min: 0.02    15 Min: 0.02    30 Min: 0.02
                first_line = f.readline().strip().split('    ')
        except Exception as e:
            self.log.error(
                'Unable to access EventPerSecInfo'
            )
            self.log.error(e)
            return None
        for value in first_line:
            # 3 Min: 0.02
            if value.startswith(avg_time):
                # Grabs the value and converts it into float type
                return float(value.split(' ')[-1])
        return None

    def original_inline_report_queue(self):
        base_path = join('data', 'eventdb')
        customer_paths = self.util_find_paths_startwith(base_path, 'CUSTOMER_')

        # Counts the report files in the various directories and returns it as
        # a metric
        file_count = 0
        for path in customer_paths:
            original_path = join(path, 'report', 'original', 'new')
            file_list = self.util_find_report_files(original_path)
            file_count += len(file_list)
        return file_count

    def i_inline_report_queue(self, i_type):
        base_path = join('data', 'eventdb')
        customer_paths = self.util_find_paths_startwith(base_path, 'CUSTOMER_')

        # Makes a list of the paths of the report files in the various
        # directories
        report_paths = []
        for path in customer_paths:
            i_path = join(path, 'report', i_type, 'new')
            report_list = self.util_find_report_files(i_path)
            for report_name in report_list:
                report_paths.append(join(i_path, report_name))

        # Counts the number of newlines in all the report files and returns it
        # as a metric
        newline_count = 0
        for report in report_paths:
            try:
                newline_count += sum(1 for line in open(report, 'r'))
            except Exception as e:
                self.log.error('Unable to access report file')
                self.log.error(e)
                pass
        return newline_count

    def util_find_paths_startwith(self, path, starts_with):
        parsed_paths = []
        try:
            dir_list = listdir(path)
        except FileNotFoundError as e:
            self.log.error('Unable to find ' + path)
            self.log.error(e)
            return parsed_paths
        for object in dir_list:
            parsed_path = join(path, object)
            if isdir(parsed_path):
                if object.startswith(starts_with):
                    parsed_paths.append(parsed_path)
        return parsed_paths

    def util_find_report_files(self, path):
        report_list = []
        try:
            file_list = listdir(path)
        except FileNotFoundError as e:
            self.log.error('Unable to find ' + path)
            self.log.error(e)
            return report_list
        for rep_file in file_list:
            if rep_file.startswith('REPT_') and rep_file.endswith('.rpt'):
                report_list.append(rep_file)
        return report_list

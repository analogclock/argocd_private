/*
  Outputs of the deployment
*/

# ICMP rule arn
output "icmp_rule_arn" {
  value       = aws_networkfirewall_rule_group.icmp_rule.arn
  description = "Icmp firewall rule arn"
}

# DNS rule arn
output "dns_rule_arn" {
  value       = aws_networkfirewall_rule_group.dns_rule.arn
  description = "Dns firewall rule arn"
}

# NTP rule arn
output "ntp_rule_arn" {
  value       = aws_networkfirewall_rule_group.ntp_rule.arn
  description = "NTP firewall rule arn"
}

# SMB rule arn
output "smb_rule_arn" {
  value       = aws_networkfirewall_rule_group.smb_rule.arn
  description = "SMB firewall rule arn"
}

# SMTP rule arn
output "smtp_rule_arn" {
  value       = aws_networkfirewall_rule_group.smtp_rule.arn
  description = "SMTP firewall rule arn"
}

# HTTP rule arn
output "http_rule_arn" {
  value       = aws_networkfirewall_rule_group.http_rule.arn
  description = "HTTP firewall rule arn"
}

# SNMP rule arn
output "snmp_rule_arn" {
  value       = aws_networkfirewall_rule_group.snmp_rule.arn
  description = "SNMP firewall rule arn"
}

# SYSLOG rule arn
output "syslog_rule_arn" {
  value       = aws_networkfirewall_rule_group.syslog_rule.arn
  description = "SYSLOG firewall rule arn"
}

# TFTP rule arn
output "tftp_rule_arn" {
  value       = aws_networkfirewall_rule_group.tftp_rule.arn
  description = "TFTP firewall rule arn"
}

# RPC rule arn
output "rpc_rule_arn" {
  value       = aws_networkfirewall_rule_group.rpc_rule.arn
  description = "RPC firewall rule arn"
}

# NETBIOS rule arn
output "netbios_tcp_rule_arn" {
  value       = aws_networkfirewall_rule_group.netbios_tcp_rule.arn
  description = "NETBIOS firewall rule arn"
}

output "netbios_udp_rule_arn" {
  value       = aws_networkfirewall_rule_group.netbios_udp_rule.arn
  description = "NETBIOS firewall rule arn"
}

# IRC rule arn
output "irc_6660_6669_rule_arn" {
  value       = aws_networkfirewall_rule_group.irc_6660_6669_rule.arn
  description = "IRC firewall rule arn"
}

# FTP rule arn
output "ftp_rule_arn" {
  value       = aws_networkfirewall_rule_group.ftp_rule.arn
  description = "FTP firewall rule arn"
}

# IMAP rule arn
output "imap_rule_arn" {
  value       = aws_networkfirewall_rule_group.imap_rule.arn
  description = "IMAP firewall rule arn"
}
# SSH rule arn
output "ssh_rule_arn" {
  value       = aws_networkfirewall_rule_group.ssh_rule.arn
  description = "SSH firewall rule arn"
}

# DHCP rule arn
output "dhcp_rule_arn" {
  value       = aws_networkfirewall_rule_group.dhcp_rule.arn
  description = "DHCP firewall rule arn"
}

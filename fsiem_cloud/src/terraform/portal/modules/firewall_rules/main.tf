
/*
Refer to protocol's assigned internet protocol number (IANA)
https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml
*/
# Pass icmp -stateless rule
resource "aws_networkfirewall_rule_group" "icmp_rule" {
  capacity = 100
  name     = "icmp-${var.fwrules_env}"
  type     = "STATELESS"
  rule_group {
    rules_source {
      stateless_rules_and_custom_actions {
        stateless_rule {
          priority = 1
          rule_definition {
            actions = ["aws:pass"]
            match_attributes {
              protocols = [1] # ICMP
              source {
                address_definition = "0.0.0.0/0"
              }
              destination {
                address_definition = "0.0.0.0/0"
              }
            }
          }
        }
      }
    }
  }
}

# Alert DNS traffic through port 53
resource "aws_networkfirewall_rule_group" "dns_rule" {
  capacity = 100
  name     = "dns-${var.fwrules_env}"
  type     = "STATEFUL"
  rule_group {
    rules_source {
      stateful_rule {
        action = "ALERT"
        header {
          destination      = "ANY"
          destination_port = "ANY"
          direction        = "ANY"
          protocol         = "DNS"
          source           = "ANY"
          source_port      = "ANY"
        }
        rule_option {
          keyword  = "sid"
          settings = ["50"]
        }
      }
    }
  }
}

# Alert NTP traffic through port 123
resource "aws_networkfirewall_rule_group" "ntp_rule" {
  capacity = 100
  name     = "ntp-${var.fwrules_env}"
  type     = "STATEFUL"
  rule_group {
    rules_source {
      stateful_rule {
        action = "ALERT"
        header {
          destination      = "ANY"
          destination_port = "ANY"
          direction        = "ANY"
          protocol         = "NTP"
          source           = "ANY"
          source_port      = "ANY"
        }
        rule_option {
          keyword  = "sid"
          settings = ["50"]
        }
      }
    }
  }
}

# Alert SMB traffic through port 445
resource "aws_networkfirewall_rule_group" "smb_rule" {
  capacity = 100
  name     = "smb-${var.fwrules_env}"
  type     = "STATEFUL"
  rule_group {
    rules_source {
      stateful_rule {
        action = "ALERT"
        header {
          destination      = "ANY"
          destination_port = "ANY"
          direction        = "ANY"
          protocol         = "SMB"
          source           = "ANY"
          source_port      = "ANY"
        }
        rule_option {
          keyword  = "sid"
          settings = ["50"]
        }
      }
    }
  }
}

# Alert SMTP traffic through port 25 ,587
resource "aws_networkfirewall_rule_group" "smtp_rule" {
  capacity = 100
  name     = "smtp-${var.fwrules_env}"
  type     = "STATEFUL"
  rule_group {
    rules_source {
      stateful_rule {
        action = "ALERT"
        header {
          destination      = "ANY"
          destination_port = "ANY"
          direction        = "ANY"
          protocol         = "SMTP"
          source           = "ANY"
          source_port      = "ANY"
        }
        rule_option {
          keyword  = "sid"
          settings = ["50"]
        }
      }
    }
  }
}

# Alert HTTP traffic(TCP) through port 80
resource "aws_networkfirewall_rule_group" "http_rule" {
  capacity = 100
  name     = "http-${var.fwrules_env}"
  type     = "STATEFUL"
  rule_group {
    rules_source {
      stateful_rule {
        action = "ALERT"
        header {
          destination      = "ANY"
          destination_port = "80"
          direction        = "ANY"
          protocol         = "HTTP"
          source           = "ANY"
          source_port      = "ANY"
        }
        rule_option {
          keyword  = "sid"
          settings = ["50"]
        }
      }
    }
  }
}

# Alert SNMP traffic(UDP) through port 161 & 162
resource "aws_networkfirewall_rule_group" "snmp_rule" {
  capacity = 100
  name     = "snmp-${var.fwrules_env}"
  type     = "STATEFUL"
  rule_group {
    rules_source {
      stateful_rule {
        action = "ALERT"
        header {
          destination      = "ANY"
          destination_port = "161:162"
          direction        = "ANY"
          protocol         = "UDP"
          source           = "ANY"
          source_port      = "ANY"
        }
        rule_option {
          keyword  = "sid"
          settings = ["50"]
        }
      }
    }
  }
}

# Alert SYSLOG traffic(UDP) through port 514
resource "aws_networkfirewall_rule_group" "syslog_rule" {
  capacity = 100
  name     = "syslog-${var.fwrules_env}"
  type     = "STATEFUL"
  rule_group {
    rules_source {
      stateful_rule {
        action = "ALERT"
        header {
          destination      = "ANY"
          destination_port = "514"
          direction        = "ANY"
          protocol         = "UDP"
          source           = "ANY"
          source_port      = "ANY"
        }
        rule_option {
          keyword  = "sid"
          settings = ["50"]
        }
      }
    }
  }
}

# Alert TFTP traffic(UDP) through port 69
resource "aws_networkfirewall_rule_group" "tftp_rule" {
  capacity = 100
  name     = "tftp-${var.fwrules_env}"
  type     = "STATEFUL"
  rule_group {
    rules_source {
      stateful_rule {
        action = "ALERT"
        header {
          destination      = "ANY"
          destination_port = "ANY"
          direction        = "ANY"
          protocol         = "TFTP"
          source           = "ANY"
          source_port      = "ANY"
        }
        rule_option {
          keyword  = "sid"
          settings = ["50"]
        }
      }
    }
  }
}

# Alert MS RPC traffic(TCP/UDP) through port 135
resource "aws_networkfirewall_rule_group" "rpc_rule" {
  capacity = 100
  name     = "rpc-${var.fwrules_env}"
  type     = "STATEFUL"
  rule_group {
    rules_source {
      stateful_rule {
        action = "ALERT"
        header {
          destination      = "ANY"
          destination_port = "ANY"
          direction        = "ANY"
          protocol         = "DCERPC"
          source           = "ANY"
          source_port      = "ANY"
        }
        rule_option {
          keyword  = "sid"
          settings = ["50"]
        }
      }
    }
  }
}
# Alert NETBIOS traffic(TCP/UDP) through port 137 to 139
resource "aws_networkfirewall_rule_group" "netbios_tcp_rule" {
  capacity = 100
  name     = "netbios-tcp-${var.fwrules_env}"
  type     = "STATEFUL"
  rule_group {
    rules_source {
      stateful_rule {
        action = "ALERT"
        header {
          destination      = "ANY"
          destination_port = "137:139"
          direction        = "ANY"
          protocol         = "TCP"
          source           = "ANY"
          source_port      = "ANY"
        }
        rule_option {
          keyword  = "sid"
          settings = ["50"]
        }
      }
    }
  }
}

resource "aws_networkfirewall_rule_group" "netbios_udp_rule" {
  capacity = 100
  name     = "netbios-udp-${var.fwrules_env}"
  type     = "STATEFUL"
  rule_group {
    rules_source {
      stateful_rule {
        action = "ALERT"
        header {
          destination      = "ANY"
          destination_port = "137:139"
          direction        = "ANY"
          protocol         = "UDP"
          source           = "ANY"
          source_port      = "ANY"
        }
        rule_option {
          keyword  = "sid"
          settings = ["50"]
        }
      }
    }
  }
}
# Alert IRC traffic
resource "aws_networkfirewall_rule_group" "irc_6660_6669_rule" {
  name     = "irc-${var.fwrules_env}"
  capacity = 100
  type     = "STATEFUL"
  rule_group {
    rules_source {
      stateful_rule {
        action = "ALERT"
        header {
          destination      = "ANY"
          destination_port = "6660:6669"
          direction        = "ANY"
          protocol         = "TCP"
          source           = "ANY"
          source_port      = "ANY"
        }
        rule_option {
          keyword  = "sid"
          settings = ["50"]
        }
      }
    }
  }
}

# Alert FTP traffic through port 21
resource "aws_networkfirewall_rule_group" "ftp_rule" {
  capacity = 100
  name     = "ftp-${var.fwrules_env}"
  type     = "STATEFUL"
  rule_group {
    rules_source {
      stateful_rule {
        action = "ALERT"
        header {
          destination      = "ANY"
          destination_port = "ANY"
          direction        = "ANY"
          protocol         = "FTP"
          source           = "ANY"
          source_port      = "ANY"
        }
        rule_option {
          keyword  = "sid"
          settings = ["50"]
        }
      }
    }
  }
}

# Alert IMAP traffic through port 143
resource "aws_networkfirewall_rule_group" "imap_rule" {
  capacity = 100
  name     = "imap-${var.fwrules_env}"
  type     = "STATEFUL"
  rule_group {
    rules_source {
      stateful_rule {
        action = "ALERT"
        header {
          destination      = "ANY"
          destination_port = "ANY"
          direction        = "ANY"
          protocol         = "IMAP"
          source           = "ANY"
          source_port      = "ANY"
        }
        rule_option {
          keyword  = "sid"
          settings = ["50"]
        }
      }
    }
  }
}

# Alert SSH traffic through port 22
resource "aws_networkfirewall_rule_group" "ssh_rule" {
  capacity = 100
  name     = "ssh-${var.fwrules_env}"
  type     = "STATEFUL"
  rule_group {
    rules_source {
      stateful_rule {
        action = "ALERT"
        header {
          destination      = "ANY"
          destination_port = "ANY"
          direction        = "ANY"
          protocol         = "SSH"
          source           = "ANY"
          source_port      = "ANY"
        }
        rule_option {
          keyword  = "sid"
          settings = ["50"]
        }
      }
    }
  }
}

# Alert DHCP traffic through port 67
resource "aws_networkfirewall_rule_group" "dhcp_rule" {
  capacity = 100
  name     = "dhcp-${var.fwrules_env}"
  type     = "STATEFUL"
  rule_group {
    rules_source {
      stateful_rule {
        action = "ALERT"
        header {
          destination      = "ANY"
          destination_port = "ANY"
          direction        = "ANY"
          protocol         = "DHCP"
          source           = "ANY"
          source_port      = "ANY"
        }
        rule_option {
          keyword  = "sid"
          settings = ["50"]
        }
      }
    }
  }
}

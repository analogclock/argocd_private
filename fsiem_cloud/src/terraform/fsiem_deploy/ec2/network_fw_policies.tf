/*
AWS Network firewall policy.
Network firewall rules arn are defined in the portal and mapped in the vars.tf file.
The arns will change when the firewall rule name changes.
*/

resource "aws_networkfirewall_firewall_policy" "anfw_policy" {
  count = var.has_nfw ? 1 : 0
  name  = "${var.serial_number}-fwpol-${var.environment}"

  firewall_policy {
    # Stateless configuration
    stateless_default_actions          = ["aws:forward_to_sfe"]
    stateless_fragment_default_actions = ["aws:forward_to_sfe"]

    stateless_rule_group_reference {
      priority     = 10
      resource_arn = local.nfw_sl_rules_arn["icmp"]
    }

    stateful_rule_group_reference {
      resource_arn = local.nfw_sf_rules_arn["dns"]
    }
    stateful_rule_group_reference {
      resource_arn = local.nfw_sf_rules_arn["ntp"]
    }

    stateful_rule_group_reference {
      resource_arn = local.nfw_sf_rules_arn["smb"]
    }

    stateful_rule_group_reference {
      resource_arn = local.nfw_sf_rules_arn["smtp"]
    }

    stateful_rule_group_reference {
      resource_arn = local.nfw_sf_rules_arn["http"]
    }
    stateful_rule_group_reference {
      resource_arn = local.nfw_sf_rules_arn["snmp"]
    }

    stateful_rule_group_reference {
      resource_arn = local.nfw_sf_rules_arn["slog"]
    }

    stateful_rule_group_reference {
      resource_arn = local.nfw_sf_rules_arn["tftp"]
    }

    stateful_rule_group_reference {
      resource_arn = local.nfw_sf_rules_arn["rpc"]
    }

    stateful_rule_group_reference {
      resource_arn = local.nfw_sf_rules_arn["nbtcp"]
    }

    stateful_rule_group_reference {
      resource_arn = local.nfw_sf_rules_arn["nbudp"]
    }

    stateful_rule_group_reference {
      resource_arn = local.nfw_sf_rules_arn["irc"]
    }

    stateful_rule_group_reference {
      resource_arn = local.nfw_sf_rules_arn["ftp"]
    }

    stateful_rule_group_reference {
      resource_arn = local.nfw_sf_rules_arn["imap"]
    }

    stateful_rule_group_reference {
      resource_arn = local.nfw_sf_rules_arn["dhcp"]
    }
  }
}

/*
CloudWatch logging configuration
Netflow traffic logged to flow logsgroup
Alert for stateful rules logged to alert logsgroup
*/
/*
Loginsight query examples
-----------------------example query1--------------------------------------------
Fields @timestamp, event.src_ip, event.dest_ip, event.app_proto
| sort @timestamp desc
| filter event.app_proto = 'ntp'

*/

resource "aws_networkfirewall_logging_configuration" "anfw_alert_logging_configuration" {
  count        = var.has_nfw ? 1 : 0
  firewall_arn = aws_networkfirewall_firewall.anfw[0].arn
  logging_configuration {
    log_destination_config {
      log_destination = {
        logGroup = aws_cloudwatch_log_group.anfw_alert_log_group[0].name
      }
      log_destination_type = "CloudWatchLogs"
      log_type             = "ALERT"
    }
    log_destination_config {
      log_destination = {
        logGroup = aws_cloudwatch_log_group.anfw_flow_log_group[0].name
      }
      log_destination_type = "CloudWatchLogs"
      log_type             = "FLOW"
    }
  }
}

# CloudWatch log group (netflow)
resource "aws_cloudwatch_log_group" "anfw_flow_log_group" {
  count             = var.has_nfw ? 1 : 0
  name              = "fsiem-firewall-flow-${var.serial_number}-${var.environment}"
  retention_in_days = local.log_persistance_days_short
}

# CloudWatch Log Group (alert)
resource "aws_cloudwatch_log_group" "anfw_alert_log_group" {
  count             = var.has_nfw ? 1 : 0
  name              = "fsiem-firewall-alert-${var.serial_number}-${var.environment}"
  retention_in_days = local.log_persistance_days_short
}

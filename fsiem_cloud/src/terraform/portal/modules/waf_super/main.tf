/*
  WAF ACL (Web Application Firewall Access Control List) that sits in front of the portal cloudfront to protect it against malicious traffic.
  https://docs.aws.amazon.com/waf/latest/developerguide/aws-managed-rule-groups-list.html
*/

locals {
  waf_super_name = "waf_super_${var.environment}"
}
resource "aws_wafv2_regex_pattern_set" "waf_api_regex_pattern_set" {
  name        = "waf_api_regex_pattern_set_${var.environment}"
  description = "Restict api external access regex pattern set"
  scope       = "REGIONAL"

  regular_expression {
    regex_string = "/phoenix/rest/h5/sys/config/clickhouse"
  }
  regular_expression {
    regex_string = "/phoenix/rest/h5/sys/config/archive"
  }
  regular_expression {
    regex_string = "/phoenix/rest/h5/server/worker/op"
  }
  regular_expression {
    regex_string = "/phoenix/uploadLicense"
  }
}

# Rules for restricting api access
resource "aws_wafv2_rule_group" "waf_api_rule_group" {
  name     = "waf_api_access_rule_group_${var.environment}"
  scope    = "REGIONAL"
  capacity = 100
  rule {
    name     = "waf_api_access_rule_rg"
    priority = 1
    action {
      block {}
    }
    statement {
      regex_pattern_set_reference_statement {
        arn = aws_wafv2_regex_pattern_set.waf_api_regex_pattern_set.arn
        field_to_match {
          uri_path {}
        }
        text_transformation {
          priority = 0
          type     = "NONE"
        }
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "waf_api_metric"
      sampled_requests_enabled   = true
    }
  }
  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "waf_api_rg_metric"
    sampled_requests_enabled   = true
  }

}

# WAF that goes in front of the super
resource "aws_wafv2_web_acl" "waf_super" {
  name  = local.waf_super_name
  scope = "REGIONAL"

  default_action {
    allow {}
  }

  rule {
    name     = "aws_common"
    priority = 1

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
        rule_action_override {
          name = "NoUserAgent_HEADER"
          action_to_use {
            count {}
          }
        }
        rule_action_override {
          name = "CrossSiteScripting_BODY"
          action_to_use {
            count {}
          }
        }
        rule_action_override {
          name = "EC2MetaDataSSRF_BODY"
          action_to_use {
            count {}
          }
        }
        rule_action_override {
          name = "SizeRestrictions_BODY"
          action_to_use {
            count {}
          }
        }
        rule_action_override {
          name = "GenericRFI_BODY"
          action_to_use {
            count {}
          }
        }
        rule_action_override {
          name = "GenericLFI_BODY"
          action_to_use {
            count {}
          }
        }
        rule_action_override {
          name = "SizeRestrictions_QUERYSTRING"
          action_to_use {
            count {}
          }
        }
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${local.waf_super_name}_aws_common"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "aws_bad_inputs"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
        rule_action_override {
          name = "JavaDeserializationRCE_BODY"
          action_to_use {
            count {}
          }
        }
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${local.waf_super_name}_aws_bad_inputs"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "aws_admin_protection"
    priority = 3

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesAdminProtectionRuleSet"
        vendor_name = "AWS"
        rule_action_override {
          name = "AdminProtection_URIPATH"
          action_to_use {
            count {}
          }
        }
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${local.waf_super_name}_aws_admin_protection"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "aws_ip_reputation"
    priority = 4

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesAmazonIpReputationList"
        vendor_name = "AWS"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${local.waf_super_name}_aws_ip_reputation"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "aws_anonymous_ip"
    priority = 5

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesAnonymousIpList"
        vendor_name = "AWS"
        rule_action_override {
          name = "HostingProviderIPList"
          action_to_use {
            count {}
          }
        }
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${local.waf_super_name}_aws_anonymous_ip"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "aws_sql_db"
    priority = 6

    override_action {
      count {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesSQLiRuleSet"
        vendor_name = "AWS"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${local.waf_super_name}_aws_sql_db"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "aws_linux"
    priority = 7

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesLinuxRuleSet"
        vendor_name = "AWS"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${local.waf_super_name}_aws_linux"
      sampled_requests_enabled   = true
    }
  }
  rule {
    name     = "waf_api_access_rule_wacl"
    priority = 8

    override_action {
      none {}
    }

    statement {
      rule_group_reference_statement {
        arn = aws_wafv2_rule_group.waf_api_rule_group.arn
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${local.waf_super_name}_api_access_wacl"
      sampled_requests_enabled   = true
    }
  }


  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = local.waf_super_name
    sampled_requests_enabled   = true
  }
}
/*
--------example1 loginsights query-----------
fields @timestamp, @message, @logStream, @log
| filter @message like /BLOCK/
| limit 5
---------example2 loginsights query-----------
fields @timestamp, @message, @logStream, @log
| filter @message like '/clickhouse/test'
| limit 5
*/

resource "aws_cloudwatch_log_group" "waf_super" {
  name              = "aws-waf-logs-${local.waf_super_name}"
  retention_in_days = var.retention_in_days
}

resource "aws_wafv2_web_acl_logging_configuration" "waf_super" {
  log_destination_configs = [aws_cloudwatch_log_group.waf_super.arn]
  resource_arn            = aws_wafv2_web_acl.waf_super.arn
  redacted_fields {
    single_header {
      name = "authorization"
    }
  }
  redacted_fields {
    single_header {
      name = "cookie"
    }
  }
}

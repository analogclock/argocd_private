/*
  WAF ACL (Web Application Firewall Access Control List) that sits in front of the portal cloudfront to protect it against malicious traffic.
  https://docs.aws.amazon.com/waf/latest/developerguide/aws-managed-rule-groups-list.html
*/

# WAF that goes in front of cloudfront
resource "aws_wafv2_web_acl" "waf_cloudfront" {
  name  = local.waf_cloudfront_name
  scope = "CLOUDFRONT"

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
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${local.waf_cloudfront_name}_aws_common"
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
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${local.waf_cloudfront_name}_aws_bad_inputs"
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
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${local.waf_cloudfront_name}_aws_admin_protection"
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
      metric_name                = "${local.waf_cloudfront_name}_aws_ip_reputation"
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
      metric_name                = "${local.waf_cloudfront_name}_aws_anonymous_ip"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "block_sanctioned_countries"
    priority = 6

    action {
      block {}
    }

    statement {
      geo_match_statement {
        # Belarus, Cuba, Eritrea, Iran, North Korea, Syria, Venezuela
        country_codes = ["BY", "CU", "ER", "IR", "KP", "SY", "VE"]
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${local.waf_cloudfront_name}_block_sanctioned_countries"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = local.waf_cloudfront_name
    sampled_requests_enabled   = true
  }
}

resource "aws_cloudwatch_log_group" "waf_cloudfront" {
  name              = "aws-waf-logs-${local.waf_cloudfront_name}"
  retention_in_days = local.log_persistance_days_long
}

resource "aws_wafv2_web_acl_logging_configuration" "waf_cloudfront" {
  log_destination_configs = [aws_cloudwatch_log_group.waf_cloudfront.arn]
  resource_arn            = aws_wafv2_web_acl.waf_cloudfront.arn
}

# WAF that goes in front of the API gateway
resource "aws_wafv2_web_acl" "waf_api" {
  name  = local.waf_api_name
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
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${local.waf_api_name}_aws_common"
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
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${local.waf_api_name}_aws_bad_inputs"
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
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${local.waf_api_name}_aws_admin_protection"
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
      metric_name                = "${local.waf_api_name}_aws_ip_reputation"
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
      metric_name                = "${local.waf_api_name}_aws_anonymous_ip"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "block_sanctioned_countries"
    priority = 6

    action {
      block {}
    }

    statement {
      geo_match_statement {
        # Belarus, Cuba, Eritrea, Iran, North Korea, Syria, Venezuela
        country_codes = ["BY", "CU", "ER", "IR", "KP", "SY", "VE"]
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${local.waf_api_name}_block_sanctioned_countries"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = local.waf_api_name
    sampled_requests_enabled   = true
  }
}

resource "aws_cloudwatch_log_group" "waf_api" {
  name              = "aws-waf-logs-${local.waf_api_name}"
  retention_in_days = local.log_persistance_days_long
}

resource "aws_wafv2_web_acl_logging_configuration" "waf_api" {
  log_destination_configs = [aws_cloudwatch_log_group.waf_api.arn]
  resource_arn            = aws_wafv2_web_acl.waf_api.arn
  redacted_fields {
    single_header {
      name = "authorization"
    }
  }
}

# Puts the WAF in front of the API gateway
resource "aws_wafv2_web_acl_association" "api_gateway" {
  resource_arn = aws_api_gateway_stage.stage.arn
  web_acl_arn  = aws_wafv2_web_acl.waf_api.arn
}

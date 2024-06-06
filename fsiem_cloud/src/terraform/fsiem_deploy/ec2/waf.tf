/*
  Associates the supers load balancer with the WAF deployed by portal
*/

# This gives us the full ARN for the WAF ACL in this region with just its name
data "aws_wafv2_web_acl" "waf_super" {
  name  = local.waf_super
  scope = "REGIONAL"
}

resource "aws_wafv2_web_acl_association" "waf_super" {
  resource_arn = aws_lb.super_alb.arn
  web_acl_arn  = data.aws_wafv2_web_acl.waf_super.arn
}

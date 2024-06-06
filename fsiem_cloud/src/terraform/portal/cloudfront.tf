/*
  Cloudfront portal to serve the portals static files for UI
*/
locals {
  s3_origin_id = "fsiemportal"
  index_doc    = "index.html"
}

resource "aws_cloudfront_origin_access_identity" "access_identity" {
  comment = "CloudFront Access Identity for the FortiSIEM portal"
}

resource "aws_cloudfront_distribution" "portal_distribution" {
  # depends_on = [aws_acm_certificate_validation.cert]
  enabled             = true
  http_version        = "http2"
  default_root_object = local.index_doc
  is_ipv6_enabled     = true
  aliases             = [var.domain_name]
  logging_config {
    include_cookies = false
    bucket          = aws_s3_bucket.portal_log_bucket.bucket_domain_name
    prefix          = "portal-logs"
  }
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  custom_error_response {
    error_caching_min_ttl = 0
    error_code            = 403
    response_code         = 200
    response_page_path    = "/${local.index_doc}"
  }
  # The following custom_error_responses are to ensure that errors are redirected to the angular site, sitting at index.html
  # they are required to ensure that they are routed within angular, and not by the cloudfront distribution
  custom_error_response {
    error_caching_min_ttl = 0
    error_code            = 404
    response_code         = 200
    response_page_path    = "/${local.index_doc}"
  }
  default_cache_behavior {
    allowed_methods = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods  = ["HEAD", "GET"]
    forwarded_values {
      query_string = true
      headers      = ["Authorization"]
      cookies {
        forward = "all"
      }
    }
    lambda_function_association {
      event_type   = "viewer-request"
      lambda_arn   = aws_lambda_function.url_redirect.qualified_arn
      include_body = true
    }
    target_origin_id           = local.s3_origin_id
    viewer_protocol_policy     = "redirect-to-https"
    compress                   = true
    response_headers_policy_id = aws_cloudfront_response_headers_policy.owasp.id
  }
  origin {
    domain_name = aws_s3_bucket.portal_bucket.bucket_domain_name
    origin_id   = local.s3_origin_id
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.access_identity.cloudfront_access_identity_path
    }
  }
  viewer_certificate {
    acm_certificate_arn            = var.cert_arn
    minimum_protocol_version       = "TLSv1.2_2021"
    ssl_support_method             = "sni-only"
    cloudfront_default_certificate = false
  }
  web_acl_id = aws_wafv2_web_acl.waf_cloudfront.arn
}

// TODO add more restrictions
// see https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudfront_response_headers_policy
// Test after every policy change, use dev console in a browser to see if any resource
// was blocked by this policies.
resource "aws_cloudfront_response_headers_policy" "owasp" {
  name = "owasp-${var.environment}"
  security_headers_config {
    frame_options {
      frame_option = "DENY"
      override     = true
    }
    strict_transport_security {
      access_control_max_age_sec = 31536000 # 1 year in seconds
      include_subdomains         = true
      override                   = true
    }
    content_security_policy {
      content_security_policy = "default-src 'self'; script-src 'self' 'unsafe-inline' https://${var.domain_name} ${aws_api_gateway_deployment.deployment.invoke_url}; style-src 'self' 'unsafe-inline' ${aws_api_gateway_deployment.deployment.invoke_url}; connect-src 'self' 'unsafe-inline' ${aws_api_gateway_deployment.deployment.invoke_url} https://cognito-idp.us-east-1.amazonaws.com https://${aws_cognito_user_pool.forticloud.domain}.auth.${var.region}.amazoncognito.com; img-src 'self' https://${var.domain_name} data:"
      override                = true
    }
  }
}

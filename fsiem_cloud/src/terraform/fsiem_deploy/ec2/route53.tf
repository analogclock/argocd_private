/*
  Route53 resources for domain naming
*/
resource "aws_route53_record" "worker" {
  zone_id = var.hosted_zone_id[var.environment]
  name    = "worker-${var.serial_number}.${var.hosted_zone_name[var.environment]}"
  type    = "A"

  alias {
    name                   = aws_lb.worker_alb.dns_name
    zone_id                = aws_lb.worker_alb.zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "worker_ipv6" {
  zone_id = var.hosted_zone_id[var.environment]
  name    = "worker-${var.serial_number}.${var.hosted_zone_name[var.environment]}"
  type    = "AAAA"

  alias {
    name                   = aws_lb.worker_alb.dns_name
    zone_id                = aws_lb.worker_alb.zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "super" {
  zone_id = var.hosted_zone_id[var.environment]
  name    = "${var.serial_number}.${var.hosted_zone_name[var.environment]}"
  type    = "A"

  alias {
    name                   = aws_lb.super_alb.dns_name
    zone_id                = aws_lb.super_alb.zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "super_ipv6" {
  zone_id = var.hosted_zone_id[var.environment]
  name    = "${var.serial_number}.${var.hosted_zone_name[var.environment]}"
  type    = "AAAA"

  alias {
    name                   = aws_lb.super_alb.dns_name
    zone_id                = aws_lb.super_alb.zone_id
    evaluate_target_health = false
  }
}

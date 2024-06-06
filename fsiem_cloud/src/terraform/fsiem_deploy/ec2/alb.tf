/*
  Load balancers to serve components externally
*/

locals {
  ssl_policy = "ELBSecurityPolicy-FS-1-2-Res-2020-10"
}

data "aws_acm_certificate" "wildcard_environment" {
  domain      = "*.${var.hosted_zone_name[var.environment]}"
  types       = ["AMAZON_ISSUED"]
  statuses    = ["ISSUED"]
  most_recent = true
  key_types   = ["RSA_2048"]
}

# Worker ALB
resource "aws_lb" "worker_alb" {
  name               = "${var.serial_number}-worker-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.worker_alb.id]
  subnets            = module.vpc.public_subnets
  ip_address_type    = "dualstack"
}

resource "aws_lb_target_group" "worker" {
  name        = "${var.serial_number}-worker-alb-tg"
  target_type = "instance"
  vpc_id      = module.vpc.vpc_id
  port        = 443
  protocol    = "HTTPS"
  health_check {
    protocol            = "HTTPS"
    path                = "/"
    interval            = 20
    timeout             = 10
    healthy_threshold   = 2
    unhealthy_threshold = 5
  }
}

resource "aws_lb_listener" "worker" {
  load_balancer_arn = aws_lb.worker_alb.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = local.ssl_policy
  certificate_arn   = data.aws_acm_certificate.wildcard_environment.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.worker.arn
  }
}

resource "aws_autoscaling_attachment" "worker" {
  autoscaling_group_name = aws_autoscaling_group.worker_ingestion.id
  lb_target_group_arn    = aws_lb_target_group.worker.id
}

resource "aws_lb_target_group_attachment" "worker" {
  count            = var.data_workers
  target_group_arn = aws_lb_target_group.worker.arn
  target_id        = aws_instance.worker[count.index].id
  port             = 443
}

# Super ALB
resource "aws_lb" "super_alb" {
  name               = "${var.serial_number}-super-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.super_alb.id]
  subnets            = module.vpc.public_subnets
  ip_address_type    = "dualstack"
}

resource "aws_lb_target_group" "super" {
  name        = "${var.serial_number}-super-alb-tg"
  target_type = "instance"
  vpc_id      = module.vpc.vpc_id
  port        = 443
  protocol    = "HTTPS"
  health_check {
    protocol            = "HTTPS"
    path                = "/"
    interval            = 20
    timeout             = 10
    healthy_threshold   = 2
    unhealthy_threshold = 5
  }
}

resource "aws_lb_listener" "super" {
  load_balancer_arn = aws_lb.super_alb.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = local.ssl_policy
  certificate_arn   = data.aws_acm_certificate.wildcard_environment.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.super.arn
  }
}

resource "aws_lb_target_group_attachment" "super" {
  target_group_arn = aws_lb_target_group.super.arn
  target_id        = aws_instance.super.id
  port             = 443
}

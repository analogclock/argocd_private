/*
  Update Super and Worker ALB's with the additional MSSP's ssl certificate.
  This is to support an alternate domain.
*/

# Super ALB
resource "aws_lb_listener_certificate" "super_mssp_cert" {
  count           = local.has_alternate_certificiate ? 1 : 0
  listener_arn    = aws_lb_listener.super.arn
  certificate_arn = var.alternate_domain_certificate_arn
}

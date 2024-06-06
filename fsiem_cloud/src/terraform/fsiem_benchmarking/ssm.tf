/*
  SSM: automation that interacts with AWS resources as well as
  runs scripts on the instances.
*/
resource "aws_ssm_document" "fsiem_bm_register_collectors" {
  name            = "fsiem_bm_register_collectors_${var.environment}"
  document_format = "YAML"
  document_type   = "Automation"
  content = templatefile("yaml/fsiem_register_collector.yaml",
    {
      assume_role = aws_iam_role.fsiem_bm_ssm_role.arn
      environment = var.environment
    }
  )
}

resource "aws_ssm_document" "fsiem_bm_generate_events" {
  name            = "fsiem_bm_generate_events_${var.environment}"
  document_format = "YAML"
  document_type   = "Automation"
  content = templatefile("yaml/fsiem_generate_events.yaml",
    {
      assume_role = aws_iam_role.fsiem_bm_ssm_role.arn
      environment = var.environment
    }
  )
}

resource "aws_ssm_document" "fsiem_bm_stop_events" {
  name            = "fsiem_bm_stop_events_${var.environment}"
  document_format = "YAML"
  document_type   = "Automation"
  content = templatefile("yaml/fsiem_stop_events.yaml",
    {
      assume_role = aws_iam_role.fsiem_bm_ssm_role.arn
      environment = var.environment
    }
  )
}


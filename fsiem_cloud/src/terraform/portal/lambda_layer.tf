# Defines re-usable lambda layers.

# fsiem_api_client project as a lambda layer
resource "aws_lambda_layer_version" "layer_fsiem_api_client" {
  filename            = var.layer_fsiem_api_client_zip
  source_code_hash    = filebase64sha256(var.layer_fsiem_api_client_zip)
  layer_name          = "layer_fsiem_api_client_${var.environment}"
  compatible_runtimes = [local.runtime_python_lambda]
}

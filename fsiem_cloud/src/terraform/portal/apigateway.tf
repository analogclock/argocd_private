/*
  This file creates an AWS API Gateway. It redirects incoming requests to the
  api lambda function.

  NOTE: be careful with any changes here, as this is tied in with FortiCloud.
        Things like URLs and id will need to be re-synced with FortiCloud and
        a new deployment will generate a >new id<.

*/
resource "aws_api_gateway_rest_api" "rest_api" {
  name                     = local.gateway_name
  minimum_compression_size = 500
  endpoint_configuration {
    types = ["EDGE"]
  }
}

data "aws_iam_policy_document" "api_policy" {
  statement {
    actions = ["execute-api:Invoke"]
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    resources = ["execute-api:/*"]
  }
}

resource "aws_api_gateway_rest_api_policy" "rest_api_policy" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  policy      = data.aws_iam_policy_document.api_policy.json
}

resource "aws_api_gateway_resource" "proxy_var" {
  parent_id   = aws_api_gateway_rest_api.rest_api.root_resource_id
  path_part   = "{proxy+}"
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
}

resource "aws_api_gateway_method" "proxy_var_options" {
  resource_id   = aws_api_gateway_resource.proxy_var.id
  rest_api_id   = aws_api_gateway_rest_api.rest_api.id
  authorization = "NONE"
  http_method   = "OPTIONS"
}

resource "aws_api_gateway_method_response" "response_200" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  resource_id = aws_api_gateway_resource.proxy_var.id
  http_method = aws_api_gateway_method.proxy_var_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"      = true
    "method.response.header.Access-Control-Allow-Headers"     = true
    "method.response.header.Access-Control-Allow-Methods"     = true
    "method.response.header.Access-Control-Allow-Credentials" = true
  }
}

resource "aws_api_gateway_integration" "options_mock" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  resource_id = aws_api_gateway_resource.proxy_var.id
  http_method = aws_api_gateway_method.proxy_var_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{statusCode:200}"
  }
  content_handling = "CONVERT_TO_TEXT"
}

resource "aws_api_gateway_integration_response" "mock_200" {
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
  resource_id = aws_api_gateway_resource.proxy_var.id
  http_method = aws_api_gateway_method.proxy_var_options.http_method
  status_code = aws_api_gateway_method_response.response_200.status_code
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"      = "'*'",
    "method.response.header.Access-Control-Allow-Headers"     = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent'",
    "method.response.header.Access-Control-Allow-Methods"     = "'OPTIONS,DELETE,GET,HEAD,PATCH,POST,PUT'",
    "method.response.header.Access-Control-Allow-Credentials" = "'false'"
  }
  response_templates = {
    "application/json" = "#set($origin = $input.params(\"Origin\"))\n#if($origin == \"\") #set($origin = $input.params(\"origin\")) #end\n#if($origin.matches(\".*\")) #set($context.responseOverride.header.Access-Control-Allow-Origin = $origin) #end"
  }
}

resource "aws_api_gateway_method" "proxy_var_any" {
  resource_id      = aws_api_gateway_resource.proxy_var.id
  rest_api_id      = aws_api_gateway_rest_api.rest_api.id
  authorization    = "NONE"
  http_method      = "ANY"
  api_key_required = false
}

resource "aws_api_gateway_integration" "any_post" {
  rest_api_id             = aws_api_gateway_rest_api.rest_api.id
  resource_id             = aws_api_gateway_resource.proxy_var.id
  http_method             = aws_api_gateway_method.proxy_var_any.http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.api.invoke_arn
}

resource "aws_api_gateway_deployment" "deployment" {
  depends_on = [
    aws_api_gateway_method.proxy_var_options,
    aws_api_gateway_method.proxy_var_any
  ]
  rest_api_id = aws_api_gateway_rest_api.rest_api.id
}


resource "aws_api_gateway_stage" "stage" {
  deployment_id = aws_api_gateway_deployment.deployment.id
  rest_api_id   = aws_api_gateway_rest_api.rest_api.id
  stage_name    = "${var.environment}-stage"
}

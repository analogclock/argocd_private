/*
  Create lambda function with python scripts for ssm documents to execute in all AWS regions supported by FSIEM.
  The default region is us-east-1.
  The module lambdafunc_pyscripts is invoked here.
*/

module "lambdassm-source-us-east-1" {
  source               = "./modules/lambdafunc_pyscripts"
  type_lambda          = "zip"
  source_dir_lambda    = var.ssm_automation_src_dir
  output_path_lambda   = var.ssm_automation_lambda_zip
  function_name_lambda = "lambda_ssm_source_all_${var.environment}"
  filename_lambda      = var.ssm_automation_lambda_zip
  role_lambda          = aws_iam_role.lambda_ssm_role.arn
  runtime_lambda       = local.runtime_python_lambda
  handler_lambda       = "ssm_source_handler_all.lambda_handler"
  secret_arn           = aws_secretsmanager_secret.fortimonitor_api_key_write.arn
  secret_region        = var.region
  retention_in_days    = local.log_persistance_days_short
}

module "lambdassm-source-eu-central-1" {
  source               = "./modules/lambdafunc_pyscripts"
  type_lambda          = "zip"
  source_dir_lambda    = var.ssm_automation_src_dir
  output_path_lambda   = var.ssm_automation_lambda_zip
  function_name_lambda = "lambda_ssm_source_all_${var.environment}"
  filename_lambda      = var.ssm_automation_lambda_zip
  role_lambda          = aws_iam_role.lambda_ssm_role.arn
  runtime_lambda       = local.runtime_python_lambda
  handler_lambda       = "ssm_source_handler_all.lambda_handler"
  secret_arn           = aws_secretsmanager_secret.fortimonitor_api_key_write.arn
  secret_region        = var.region
  retention_in_days    = local.log_persistance_days_short

  providers = {
    aws = aws.eu-central-1
  }
}
module "lambdassm-source-eu-west-1" {
  source               = "./modules/lambdafunc_pyscripts"
  type_lambda          = "zip"
  source_dir_lambda    = var.ssm_automation_src_dir
  output_path_lambda   = var.ssm_automation_lambda_zip
  function_name_lambda = "lambda_ssm_source_all_${var.environment}"
  filename_lambda      = var.ssm_automation_lambda_zip
  role_lambda          = aws_iam_role.lambda_ssm_role.arn
  runtime_lambda       = local.runtime_python_lambda
  handler_lambda       = "ssm_source_handler_all.lambda_handler"
  secret_arn           = aws_secretsmanager_secret.fortimonitor_api_key_write.arn
  secret_region        = var.region
  retention_in_days    = local.log_persistance_days_short

  providers = {
    aws = aws.eu-west-1
  }
}


module "lambdassm-source-eu-west-2" {
  source               = "./modules/lambdafunc_pyscripts"
  type_lambda          = "zip"
  source_dir_lambda    = var.ssm_automation_src_dir
  output_path_lambda   = var.ssm_automation_lambda_zip
  function_name_lambda = "lambda_ssm_source_all_${var.environment}"
  filename_lambda      = var.ssm_automation_lambda_zip
  role_lambda          = aws_iam_role.lambda_ssm_role.arn
  runtime_lambda       = local.runtime_python_lambda
  handler_lambda       = "ssm_source_handler_all.lambda_handler"
  secret_arn           = aws_secretsmanager_secret.fortimonitor_api_key_write.arn
  secret_region        = var.region
  retention_in_days    = local.log_persistance_days_short

  providers = {
    aws = aws.eu-west-2
  }
}

module "lambdassm-source-eu-west-3" {
  source               = "./modules/lambdafunc_pyscripts"
  type_lambda          = "zip"
  source_dir_lambda    = var.ssm_automation_src_dir
  output_path_lambda   = var.ssm_automation_lambda_zip
  function_name_lambda = "lambda_ssm_source_all_${var.environment}"
  filename_lambda      = var.ssm_automation_lambda_zip
  role_lambda          = aws_iam_role.lambda_ssm_role.arn
  runtime_lambda       = local.runtime_python_lambda
  handler_lambda       = "ssm_source_handler_all.lambda_handler"
  secret_arn           = aws_secretsmanager_secret.fortimonitor_api_key_write.arn
  secret_region        = var.region
  retention_in_days    = local.log_persistance_days_short

  providers = {
    aws = aws.eu-west-3
  }
}

module "lambdassm-source-eu-north-1" {
  source               = "./modules/lambdafunc_pyscripts"
  type_lambda          = "zip"
  source_dir_lambda    = var.ssm_automation_src_dir
  output_path_lambda   = var.ssm_automation_lambda_zip
  function_name_lambda = "lambda_ssm_source_all_${var.environment}"
  filename_lambda      = var.ssm_automation_lambda_zip
  role_lambda          = aws_iam_role.lambda_ssm_role.arn
  runtime_lambda       = local.runtime_python_lambda
  handler_lambda       = "ssm_source_handler_all.lambda_handler"
  secret_arn           = aws_secretsmanager_secret.fortimonitor_api_key_write.arn
  secret_region        = var.region
  retention_in_days    = local.log_persistance_days_short

  providers = {
    aws = aws.eu-north-1
  }
}

module "lambdassm-source-us-east-2" {
  source               = "./modules/lambdafunc_pyscripts"
  type_lambda          = "zip"
  source_dir_lambda    = var.ssm_automation_src_dir
  output_path_lambda   = var.ssm_automation_lambda_zip
  function_name_lambda = "lambda_ssm_source_all_${var.environment}"
  filename_lambda      = var.ssm_automation_lambda_zip
  role_lambda          = aws_iam_role.lambda_ssm_role.arn
  runtime_lambda       = local.runtime_python_lambda
  handler_lambda       = "ssm_source_handler_all.lambda_handler"
  secret_arn           = aws_secretsmanager_secret.fortimonitor_api_key_write.arn
  secret_region        = var.region
  retention_in_days    = local.log_persistance_days_short

  providers = {
    aws = aws.us-east-2
  }
}

module "lambdassm-source-us-west-2" {
  source               = "./modules/lambdafunc_pyscripts"
  type_lambda          = "zip"
  source_dir_lambda    = var.ssm_automation_src_dir
  output_path_lambda   = var.ssm_automation_lambda_zip
  function_name_lambda = "lambda_ssm_source_all_${var.environment}"
  filename_lambda      = var.ssm_automation_lambda_zip
  role_lambda          = aws_iam_role.lambda_ssm_role.arn
  runtime_lambda       = local.runtime_python_lambda
  handler_lambda       = "ssm_source_handler_all.lambda_handler"
  secret_arn           = aws_secretsmanager_secret.fortimonitor_api_key_write.arn
  secret_region        = var.region
  retention_in_days    = local.log_persistance_days_short

  providers = {
    aws = aws.us-west-2
  }
}

module "lambdassm-source-ca-central-1" {
  source               = "./modules/lambdafunc_pyscripts"
  type_lambda          = "zip"
  source_dir_lambda    = var.ssm_automation_src_dir
  output_path_lambda   = var.ssm_automation_lambda_zip
  function_name_lambda = "lambda_ssm_source_all_${var.environment}"
  filename_lambda      = var.ssm_automation_lambda_zip
  role_lambda          = aws_iam_role.lambda_ssm_role.arn
  runtime_lambda       = local.runtime_python_lambda
  handler_lambda       = "ssm_source_handler_all.lambda_handler"
  secret_arn           = aws_secretsmanager_secret.fortimonitor_api_key_write.arn
  secret_region        = var.region
  retention_in_days    = local.log_persistance_days_short

  providers = {
    aws = aws.ca-central-1
  }
}

module "lambdassm-source-ap-south-1" {
  source               = "./modules/lambdafunc_pyscripts"
  type_lambda          = "zip"
  source_dir_lambda    = var.ssm_automation_src_dir
  output_path_lambda   = var.ssm_automation_lambda_zip
  function_name_lambda = "lambda_ssm_source_all_${var.environment}"
  filename_lambda      = var.ssm_automation_lambda_zip
  role_lambda          = aws_iam_role.lambda_ssm_role.arn
  runtime_lambda       = local.runtime_python_lambda
  handler_lambda       = "ssm_source_handler_all.lambda_handler"
  secret_arn           = aws_secretsmanager_secret.fortimonitor_api_key_write.arn
  secret_region        = var.region
  retention_in_days    = local.log_persistance_days_short

  providers = {
    aws = aws.ap-south-1
  }
}

module "lambdassm-source-ap-southeast-1" {
  source               = "./modules/lambdafunc_pyscripts"
  type_lambda          = "zip"
  source_dir_lambda    = var.ssm_automation_src_dir
  output_path_lambda   = var.ssm_automation_lambda_zip
  function_name_lambda = "lambda_ssm_source_all_${var.environment}"
  filename_lambda      = var.ssm_automation_lambda_zip
  role_lambda          = aws_iam_role.lambda_ssm_role.arn
  runtime_lambda       = local.runtime_python_lambda
  handler_lambda       = "ssm_source_handler_all.lambda_handler"
  secret_arn           = aws_secretsmanager_secret.fortimonitor_api_key_write.arn
  secret_region        = var.region
  retention_in_days    = local.log_persistance_days_short

  providers = {
    aws = aws.ap-southeast-1
  }
}

module "lambdassm-source-ap-southeast-2" {
  source               = "./modules/lambdafunc_pyscripts"
  type_lambda          = "zip"
  source_dir_lambda    = var.ssm_automation_src_dir
  output_path_lambda   = var.ssm_automation_lambda_zip
  function_name_lambda = "lambda_ssm_source_all_${var.environment}"
  filename_lambda      = var.ssm_automation_lambda_zip
  role_lambda          = aws_iam_role.lambda_ssm_role.arn
  runtime_lambda       = local.runtime_python_lambda
  handler_lambda       = "ssm_source_handler_all.lambda_handler"
  secret_arn           = aws_secretsmanager_secret.fortimonitor_api_key_write.arn
  secret_region        = var.region
  retention_in_days    = local.log_persistance_days_short

  providers = {
    aws = aws.ap-southeast-2
  }
}

module "lambdassm-source-me-south-1" {
  source               = "./modules/lambdafunc_pyscripts"
  type_lambda          = "zip"
  source_dir_lambda    = var.ssm_automation_src_dir
  output_path_lambda   = var.ssm_automation_lambda_zip
  function_name_lambda = "lambda_ssm_source_all_${var.environment}"
  filename_lambda      = var.ssm_automation_lambda_zip
  role_lambda          = aws_iam_role.lambda_ssm_role.arn
  runtime_lambda       = local.runtime_python_lambda
  handler_lambda       = "ssm_source_handler_all.lambda_handler"
  secret_arn           = aws_secretsmanager_secret.fortimonitor_api_key_write.arn
  secret_region        = var.region
  retention_in_days    = local.log_persistance_days_short

  providers = {
    aws = aws.me-south-1
  }
}

module "lambdassm-source-ap-east-1" {
  source               = "./modules/lambdafunc_pyscripts"
  type_lambda          = "zip"
  source_dir_lambda    = var.ssm_automation_src_dir
  output_path_lambda   = var.ssm_automation_lambda_zip
  function_name_lambda = "lambda_ssm_source_all_${var.environment}"
  filename_lambda      = var.ssm_automation_lambda_zip
  role_lambda          = aws_iam_role.lambda_ssm_role.arn
  runtime_lambda       = local.runtime_python_lambda
  handler_lambda       = "ssm_source_handler_all.lambda_handler"
  secret_arn           = aws_secretsmanager_secret.fortimonitor_api_key_write.arn
  secret_region        = var.region
  retention_in_days    = local.log_persistance_days_short

  providers = {
    aws = aws.ap-east-1
  }
}

module "lambdassm-source-af-south-1" {
  source               = "./modules/lambdafunc_pyscripts"
  type_lambda          = "zip"
  source_dir_lambda    = var.ssm_automation_src_dir
  output_path_lambda   = var.ssm_automation_lambda_zip
  function_name_lambda = "lambda_ssm_source_all_${var.environment}"
  filename_lambda      = var.ssm_automation_lambda_zip
  role_lambda          = aws_iam_role.lambda_ssm_role.arn
  runtime_lambda       = local.runtime_python_lambda
  handler_lambda       = "ssm_source_handler_all.lambda_handler"
  secret_arn           = aws_secretsmanager_secret.fortimonitor_api_key_write.arn
  secret_region        = var.region
  retention_in_days    = local.log_persistance_days_short

  providers = {
    aws = aws.af-south-1
  }
}

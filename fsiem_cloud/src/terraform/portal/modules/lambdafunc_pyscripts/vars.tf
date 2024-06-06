variable "type_lambda" {
  description = "type of archive file to create"
  default     = "zip"
}
variable "source_file_lambda" {
  description = "source file to create archive file"
  default     = ""
}
variable "source_dir_lambda" {
  description = "source directory to create archive file"
  default     = ""
}
variable "output_path_lambda" {
  description = "output path for archive file"
  default     = ""
}
variable "function_name_lambda" {
  description = "function name for lambda function"
  default     = ""
}
variable "filename_lambda" {
  description = "file name for lambda function"
  default     = ""
}
variable "source_code_hash_lambda" {
  description = "source code for lambda function"
  default     = ""
}
variable "role_lambda" {
  description = "role for lambda function"
  default     = ""
}
variable "runtime_lambda" {
  description = "runtime for lambda function"
  default     = "python3.11"
}
variable "handler_lambda" {
  description = "handler(python script) for lambda function"
  default     = ""
}
variable "timeout_lambda" {
  description = "time out for lambda function"
  default     = 300
}

variable "secret_arn" {
  description = "secret fortimonitor arn"
  default     = ""
}

variable "secret_region" {
  description = "secret region"
  default     = ""
}

variable "lambdalayers_arn" {
  description = "arns for all lambda layers to attach"
  type        = list(string)
  default     = []
}

variable "retention_in_days" {
  description = "Specifies the number of days you want to retain log events in the specified log group. Possible values are: 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, and 3653."
  type        = number
  default     = 7

  validation {
    condition     = var.retention_in_days == null ? true : contains([0, 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653], var.retention_in_days)
    error_message = "Must be 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653 or 0 (zero indicates never expire logs)."
  }
}

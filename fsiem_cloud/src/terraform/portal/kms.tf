/*
  KMS keys for encrypting various sensitive data
*/
resource "aws_kms_key" "key" {
  description              = "Encryption Key"
  enable_key_rotation      = true
  key_usage                = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
}

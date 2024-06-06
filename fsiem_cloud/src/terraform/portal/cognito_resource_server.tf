/*
  Resource server allows us to scope individual requests
  and tokens that are provided to the API
  identifier is used as the URL required (/licence)
*/
resource "aws_cognito_resource_server" "licence" {
  user_pool_id = aws_cognito_user_pool.forticloud.id

  identifier = "licence"
  name       = "licence activation"

  scope {
    scope_name        = "licence.get"
    scope_description = "get a licence file"
  }
}

resource "aws_cognito_resource_server" "status" {
  user_pool_id = aws_cognito_user_pool.forticloud.id

  identifier = "status"
  name       = "status update"

  scope {
    scope_name        = "update.post"
    scope_description = "update status for stack"
  }
}

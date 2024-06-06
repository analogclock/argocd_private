Param (
    [string]$AccessKey,
    [string]$SecretKey,
    [string]$Username,
    [string]$Rolename,
    [string]$Account,
    [string]$Token
)

# Set the main account to use from the provided input
Set-AWSCredential -AccessKey $AccessKey -SecretKey $SecretKey -StoreAs Main

# Get MFA token / session token and save it as our main
$Response = Get-STSSessionToken -SerialNumber arn:aws:iam::213560266036:mfa/$UserName -TokenCode $Token -ProfileName Main

# Set Session as the aws creds
Set-AWSCredentials -AccessKey $Response.AccessKeyId -SecretKey $Response.SecretAccessKey -SessionToken $Response.SessionToken -StoreAs Session

# Assume new Role
$Response = (Use-STSRole -Region eu-west-1 -RoleArn arn:aws:iam::${Account}:role/$Rolename -RoleSessionName 'PowershellSession' -ProfileName Session).Credentials

# Set the role based credentials
echo "Saving to $HOME/.aws/credentials to allow for shared cli/python/powershell management"
Set-AWSCredentials -AccessKey $Response.AccessKeyId -SecretKey $Response.SecretAccessKey -SessionToken $Response.SessionToken -StoreAs RoleBasedAccess -ProfileLocation "$HOME/.aws/credentials"

# Make the role based creds the default - you have now authenticated successfully and all commands should just _work_
Initialize-AWSDefaults -ProfileName RoleBasedAccess -Region eu-west-1


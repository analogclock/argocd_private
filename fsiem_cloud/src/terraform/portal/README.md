# AWS Cognito

AWS Cognito is used to provide a SAML 2.0 identity provider for the portal deployments. It acts as a broker between the UI (SP)and FortiCloud SSO (IDP).

UI - service provider (SP)
FortiCloud SSO API - Identity Provider (IDP)

## Setting up

In order to authenticate between the parties, you must exchange SP and IDP metadata.

Development metadata resides in (forticloud_dev_saml.xml).
Other environments store SP and IDP XML files in the environment deployment folders (src/terraform/portal/env/$ENV_NAME).

If you require to exchange new metadata, you must generate SP from the cognito user pool, that has been deployed.
You then take that metadata and send it on to David Lao (dlao), who return you the IDP and allow access to FortiCloud SSO.
NOTE: if you make any redeployment of the Cognito service, you must recreate the SP metadata and exchange

To recreate the SP, copy the template provided, and update the `entityID` field with the new user pool id.
Should you make a change to the domain name for the user pool also update the `SingleLogoutService` and the `AssertionConsumerService` accordingly

In order to use an alias for cloudfront (a URL that isnt the default cloudfront) you need to manually insert a certificate into AWS certificate manager.
Once that is done you will need to update the var `cert_arn` with the certs ARN.
Then update the var `domain_name` with the alias that you want to use, ensuring that the cert is valid for the URL.

To get a new certificate see [doc/ENVIRONMENTS.md](doc/ENVIRONMENTS.md)

### Testing IdP and SP flow

In order to test the flow between SP and IdP you should do the following in an incognito window:

1. Navigate to the LOGIN endpoint for Cognito: <https://<COGNITO_DOMAIN>.us-east-1.amazoncognito.com/oauth2/authorize?identity_provider=FortiCloud&redirect_uri=https://localhost:4201/login&response_type=TOKEN&client_id=<COGNITO_CLIENT_ID>&scope=aws.cognito.signin.user.admin> openid
2. Ensure you are redirect to IDP Sign In page
3. Fill in Credentials
4. Ensure you are redirected to https://localhost:4201 on successful login

## Deploying

As everything is currently in terraform, we will utilise it to deploy all aspects of the cognito broker.

1. User Pool
   - The user pool is used to provide a simple SP broker between the UI/API and FortiCloud SSO (IDP).
2. Identity Provider
    - The identity provider is used to define the IDP for SAML endpoint to use for authentication, request and response.
3. User Pool Clients
    - User Pool clients are created to separate out the SAML scopes required.
    - user_pool_client:forticloud is used by the UI.
    - user_pool_client:licence is used by a stack to generate a license file.
4. Resource Server
    - A resource server defined custom scopes, to a particular URL endpoint to lock down permissions on.

### Running

Within this root folder simply run:

To see changes which will be performed

```bash
terraform plan
```

To apply changes to existing:

```bash
terraform apply
```

To destroy current deployed entities:

```bash
terraform destroy
```

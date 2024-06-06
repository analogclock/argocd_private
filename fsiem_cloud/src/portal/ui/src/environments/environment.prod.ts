//  Application imports
import { IEnvironment } from 'app/models/environment';

export const environment: IEnvironment = {
    production: true,
    enableProdMode: true,
    provisioningApi: 'https://dgj5jqjayc.execute-api.us-east-1.amazonaws.com/prod-stage/api',
    cognitoUrl: 'https://forticloud-fsiem-prod.auth.us-east-1.amazoncognito.com',
    cognitoProvider: 'FortiCloud',
    clientId: '6bk96o51b71dq3lqve6hjmoma9',
    registerUrl: 'https://support.fortinet.com/Login/CreateAccount.aspx',
    logoutUrl: 'https://support.fortinet.com/Credentials/Login/CommonLogout.aspx',
    productName: 'FortiSIEM Cloud',
    cognitoPool: 'us-east-1_TC1vSEXNB'
};

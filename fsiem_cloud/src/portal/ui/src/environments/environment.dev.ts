//  Application imports
import { IEnvironment } from 'app/models/environment';

export const environment: IEnvironment = {
    production: false,
    enableProdMode: true,
    provisioningApi: 'https://zh71vh4fxj.execute-api.us-east-1.amazonaws.com/dev-stage/api',
    cognitoUrl: 'https://forticloud-fsiem-dev.auth.us-east-1.amazoncognito.com',
    cognitoProvider: 'FortiCloud',
    clientId: 'a0clc12gqnih678di84d7krm3',
    registerUrl: 'https://172.30.38.100/RegistrationDev/Login/CreateAccount.aspx',
    logoutUrl: 'https://support-dev.corp.fortinet.com/Credentials/Login/CommonLogout.aspx',
    productName: 'FortiSIEM Cloud',
    cognitoPool: 'us-east-1_UByCct7Nc'
};

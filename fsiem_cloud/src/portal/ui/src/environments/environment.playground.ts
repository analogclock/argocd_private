//  Application imports
import { IEnvironment } from 'app/models/environment';

export const environment: IEnvironment = {
    production: false,
    enableProdMode: true,
    provisioningApi: 'https://oo35plz18d.execute-api.us-east-1.amazonaws.com/playground-stage/api',
    cognitoUrl: 'https://forticloud-fsiem-playground.auth.us-east-1.amazoncognito.com',
    cognitoProvider: 'FortiCloud',
    clientId: 'ga33cbp9k9utouugbf2biin7s',
    registerUrl: 'https://support.fortinet.com/Login/CreateAccount.aspx',
    logoutUrl: 'https://support.fortinet.com/Credentials/Login/CommonLogout.aspx',
    productName: 'FortiSIEM Cloud',
    cognitoPool: 'us-east-1_RhzCh1viR',
};

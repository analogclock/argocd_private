//  Application imports
import { IEnvironment } from 'app/models/environment';

export const environment: IEnvironment = {
    production: false,
    provisioningApi: 'https://7w06qhfe38.execute-api.us-east-1.amazonaws.com/dev/api',
    cognitoUrl: 'https://forticloud-fsiem-dev.auth.us-east-1.amazoncognito.com',
    cognitoProvider: 'FortiCloud',
    clientId: '7atroglk4p7rvjcoisarkhhicc',
    registerUrl: 'https://172.30.38.100/RegistrationDev/Login/CreateAccount.aspx',
    productName: 'FortiSIEM',
    enableProdMode: false,
    cognitoPool: 'us-east-1_RhzCh1viR',
    logoutUrl: ''
};

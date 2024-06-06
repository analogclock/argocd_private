export interface IEnvironment {
    production: boolean;
    enableProdMode: boolean;
    provisioningApi: string;
    cognitoUrl: string;
    cognitoPool: string;
    cognitoProvider: string;
    clientId: string;
    registerUrl: string;
    logoutUrl: string;
    productName: string;
}

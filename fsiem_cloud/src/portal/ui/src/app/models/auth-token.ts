export class AuthToken {
    public static fromString(tokenStringArray: Array<string>): AuthToken {
        const authToken: AuthToken = new AuthToken();
        tokenStringArray.forEach(
            (property: string): void => {
                const keyValue: [string, string] = property.split('=') as [string, string];
                if (keyValue[0] === 'token_type') {
                    authToken.tokenType = keyValue[1];
                } else if (keyValue[0] === 'id_token') {
                    authToken.token = keyValue[1];
                } else if (keyValue[0] === 'expires_in') {
                    authToken.expiresIn = parseInt(keyValue[1], 10);
                } else if (keyValue[0] === 'state') {
                    authToken.data = keyValue[1].replace(/['"]+/g, '');
                }
            }
        );
        return authToken;
    }

    public tokenType: string;
    public token: string;
    public expiresIn: number;
    public data: string = '';
}

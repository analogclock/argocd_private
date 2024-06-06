//  Third party imports
import { deserialize } from 'cerialize';

export class RAccountDetails {
    @deserialize
    public accountCompany: string;
    @deserialize
    public accountEmail: string;
    @deserialize
    public displayEmail: string;
    @deserialize
    public accountId: number;
    @deserialize
    public allAssetsAccess: boolean;
    @deserialize
    public iamAccountName: string;
    @deserialize
    public iamUserName: string;
    @deserialize
    public isMasterUser: boolean;
    @deserialize
    public masterUserName: string;
    @deserialize
    public userAuthenticationPassed: boolean;
    @deserialize
    public userAuthenticationUrl: string;
    @deserialize
    public userEmail: string;
    @deserialize
    public userGroup: string;
    @deserialize
    public userId: number;
}

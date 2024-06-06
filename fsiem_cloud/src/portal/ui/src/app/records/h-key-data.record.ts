//  Angular imports
import { HttpParams } from '@angular/common/http';
//  Application imports
import { RAccountDetails } from './account-details.record';
//  Third party imports
import { deserializeAs, GenericDeserialize, Serialize, serializeAs } from 'cerialize';
import { environment } from 'environments/environment';

export class RSite {
    @serializeAs('app_name')
    @deserializeAs('app_name')
    public appName: string;
    @serializeAs('last_url')
    @deserializeAs('last_url')
    public lastUrl: string;
}

export class RHKeyData {

    // eslint-disable-next-line @typescript-eslint/naming-convention
    public static OnSerialized(instance: RHKeyData, pojo: any): void {
        pojo.user_fullaccess = !instance.userFullAccess ? 'True' : this.ftntBooleanString(instance.userFullAccess);
    }

    // eslint-disable-next-line @typescript-eslint/naming-convention
    public static OnDeserialized(instance: RHKeyData, pojo: any): void {
        instance.userFullAccess = this.getBoolean(pojo.user_fullaccess);
    }

    public static fromBase64Encoded(base64EncodedString: string): RHKeyData {
        base64EncodedString = base64EncodedString.replace(/['"]+/g, '');
        let decoded: string = atob(base64EncodedString);
        if (decoded.startsWith('h_key=')) {
            decoded = decoded.replace(/\+/g, '%20');
            const params: HttpParams = new HttpParams({fromString: decoded});
            const hKey: string = JSON.parse(params.get('h_key'));
            return GenericDeserialize(hKey, RHKeyData);
        }
        return null;
    }

    public static partialFromAccount(account: RAccountDetails): Partial<RHKeyData> {
        const hKeyData: RHKeyData = new RHKeyData();
        if (!!account.accountId) { hKeyData.accountId = account.accountId.toString(); }
        if (!!account.userId) { hKeyData.userId = !!account.userId ? account.userId.toString() : null; }
        if (!!account.allAssetsAccess) { hKeyData.userFullAccess = this.getBoolean(account.allAssetsAccess); }
        return hKeyData;
    }

    public static complete(hkeyPartial: Partial<RHKeyData>, hkey: RHKeyData): RHKeyData {
        if (!!hkey) {
            return Object.assign(hkey, hkeyPartial);
        }
        return Object.assign(new RHKeyData, hkeyPartial);
    }

    public static toFortinet(hKeyData: RHKeyData): any {
        if (!hKeyData) {
            return {};
        }

        hKeyData.sourceApp = environment.productName;

        return Serialize(hKeyData);
    }

    private static getBoolean(val: any): boolean {
        switch (val) {
            case true:
            case 'True':
            case 'true':
            case '1':
            case 'on':
            case 'yes':
                return true;
            default:
                return false;
        }
    }

    private static ftntBooleanString(val: boolean): string {
        if (!val) {
            return 'True';
        }

        switch (val) {
            case true:
                return 'True';
            default:
                return 'False';
        }
    }

    @serializeAs('source_app')
    @deserializeAs('source_app')
    public sourceApp: string;
    @serializeAs('account_id')
    @deserializeAs('account_id')
    public accountId: string;
    @serializeAs('user_id')
    @deserializeAs('user_id')
    public userId: string;
    // serialisation is taken care of by callback
    public userFullAccess: boolean;
    @serializeAs('partner_id')
    @deserializeAs('partner_id')
    public partnerId: string;
    @serializeAs('visited_sites')
    @deserializeAs(RSite, 'visited_sites')
    public visitedSites: Array<RSite>;

    public hasLastVisited(portalName: string): boolean {
        return !!this.visitedSites && !!this.visitedSites.find(
            (site: RSite): boolean => site.appName === portalName
        );
    }

    public getLastVisited(portalName: string): string {
        if (!this.visitedSites) { return; }
        const visited: Array<RSite> = this.visitedSites.filter((site: RSite): boolean => site.appName === portalName);
        return visited.last.lastUrl;
    }
}

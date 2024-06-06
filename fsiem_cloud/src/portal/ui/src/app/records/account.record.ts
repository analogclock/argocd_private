//  Application imports
import { RAccountDetails } from './account-details.record';
import { RMainMenuItem, RSubMenuItem } from './menu-item.record';
import { Utils } from 'app/utils';
//  Third party imports
import { deserialize, deserializeAs } from 'cerialize';

export class RAccount {
    // eslint-disable-next-line @typescript-eslint/naming-convention
    public static OnDeserialized(instance: RAccount, _: any): void {
        instance.serviceMenu.sort(Utils.sortByOrder);
        instance.supportMenu.sort(Utils.sortByOrder);
        instance.userMenu.sort(Utils.sortByOrder);
    }

    @deserializeAs(RAccountDetails)
    public details: RAccountDetails;
    @deserialize
    public logo: string;
    @deserializeAs(RMainMenuItem)
    public serviceMenu: Array<RMainMenuItem>;
    @deserializeAs(RMainMenuItem)
    public supportMenu: Array<RMainMenuItem>;
    @deserializeAs(RSubMenuItem)
    public userMenu: Array<RSubMenuItem>;
}

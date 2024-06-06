//  Application imports
import { Utils } from 'app/utils';
//  Third party imports
import { deserialize, deserializeAs, inheritSerialization } from 'cerialize';

export abstract class RMenuItem {
    @deserialize
    public description: string;
    @deserialize
    public displayName: string;
    @deserialize
    public order: number;
    @deserialize
    public url: string;
    @deserialize
    public visibility: 'ShowEnabled' | 'ShowDisabled' | undefined;
}

@inheritSerialization(RMenuItem)
export class RSubMenuItem extends RMenuItem {
    @deserialize
    public imageContent: string;
    @deserialize
    public itemId: number;
    @deserialize
    public sectionHeader: string;
}

@inheritSerialization(RMenuItem)
export class RMainMenuItem extends RMenuItem {
    // eslint-disable-next-line @typescript-eslint/naming-convention
    public static OnDeserialized(instance: RMainMenuItem, _: any): void {
        if (!!instance.items) {
            instance.items.sort(Utils.sortByOrder);
        }
    }

    @deserializeAs(RSubMenuItem)
    public items?: Array<RSubMenuItem>;
}

import { deserialize } from 'cerialize';

export class RTerm {
    @deserialize
    public startDate: string;
    @deserialize
    public endDate: string;
    @deserialize
    public expiryDays: number;
    @deserialize
    public quantity: number;
}

export class REntitlement {
    @deserialize
    public compute?: RTerm;
    @deserialize
    public onlineStorage?: RTerm;
    @deserialize
    public archiveStorage?: RTerm;

    public get isValid(): boolean {
        // we must have compute and online storage
        // both must have a quantity greater than 0
        return this.compute && this.onlineStorage
            && this.compute.quantity > 0
            && this.onlineStorage.quantity > 0;
    }
}

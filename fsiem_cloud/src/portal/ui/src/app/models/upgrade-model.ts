import { deserialize } from 'cerialize';

export class RUpgradeModel {
    @deserialize
    public serialNumber: string;
    @deserialize
    public upgradePath: string;
    @deserialize
    public scheduledLocal: string;
    @deserialize
    public status: string;
}

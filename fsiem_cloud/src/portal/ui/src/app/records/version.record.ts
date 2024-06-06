import { deserialize } from 'cerialize';

export class RVersion {
    @deserialize
    public upgradePath: string;
    @deserialize
    public currentVersion: string;
    @deserialize
    public newVersion: string;
}

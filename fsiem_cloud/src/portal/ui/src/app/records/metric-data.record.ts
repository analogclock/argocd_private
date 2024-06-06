import { deserialize } from 'cerialize';

export class RMetricData {
    @deserialize
    public key: string;
    @deserialize
    public value: number;
}

import { deserialize, deserializeAs } from 'cerialize';

export class RStorageData {
    @deserialize
    public day: string; // date of the data
    @deserialize
    public rows: number; // number of rows
    @deserialize
    public bytes: number; // size in bytes
    @deserialize
    public avgBytes: number; // size of average bytes per row
    @deserialize
    public uncompressedBytes: number; // size of uncompressed data in bytes
    @deserialize
    public avgUncompressedBytes: number; // average size of uncompressed data in bytes
}

export class RStorageDataRow {
    @deserialize
    public lastUpdated: string;

    @deserializeAs(RStorageData)
    public online: Array<RStorageData> = [];

    @deserializeAs(RStorageData)
    public archive: Array<RStorageData> = [];
}


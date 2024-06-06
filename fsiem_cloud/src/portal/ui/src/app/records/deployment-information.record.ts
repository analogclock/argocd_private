//  Application imports
import { Status } from './status.record';
//  Third party imports
import { deserialize, deserializeAs } from 'cerialize';
import { REntitlement } from './entitlement.record';

export class RDeploymentInformation {
    @deserialize
    public url: string;
    @deserialize
    public created: string;
    @deserialize
    public version: string;
    @deserialize
    public status: Status;
    @deserialize
    public deploymentType: string;
    @deserialize
    public deploymentEmail: string;
    @deserialize
    public serialNumber: string;
    @deserialize
    public workersUrl: string;
    @deserialize
    public ipV4Cidr: string;
    @deserialize
    public ipV6Cidr: string;
    @deserialize
    public displayRegion: string;
    @deserialize
    public onlineSizeUsage: number = 412;
    @deserialize
    public archiveSizeUsage: number = 422;
    @deserializeAs(REntitlement)
    public deploymentSKU: REntitlement;
    @deserialize
    public additionalContacts: string = '';
    @deserialize
    public alternateDomain: string = '';
    @deserialize
    public externalStorageDest: string = '';
    @deserialize
    public externalStorage: string = '';
}

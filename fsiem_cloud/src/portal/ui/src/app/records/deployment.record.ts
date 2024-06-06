import { deserialize, deserializeAs } from 'cerialize';
import { REntitlement } from './entitlement.record';
import { RDeploymentInformation } from './deployment-information.record';

export class RDeployment {
    @deserialize
    public serialNumber: string;
    @deserialize
    public description: string;
    @deserializeAs(REntitlement)
    public entitlement: REntitlement;
    @deserializeAs(RDeploymentInformation)
    public information: RDeploymentInformation;

    public get isEntitlementEqual(): boolean {
        return this.isComputeEqual && this.isOnlineEqual && this.isArchiveEqual;
    }

    public get isComputeEqual(): boolean {
        if (!this.entitlement?.compute || !this.information?.deploymentSKU?.compute) {
            // we have not been deployed
            // we haven't got an active SKU
            // or something has gone terribly wrong
            return true;
        }
        return this.equals(this.entitlement.compute.quantity, this.information.deploymentSKU.compute.quantity);
    }

    public get isOnlineEqual(): boolean {
        if (!this.entitlement?.onlineStorage || !this.information?.deploymentSKU?.onlineStorage) {
            // we have not been deployed
            // we haven't got an active SKU
            // or something has gone terribly wrong
            return true;
        }
        return this.equals(this.entitlement.onlineStorage.quantity, this.information.deploymentSKU.onlineStorage.quantity);
    }

    public get isArchiveEqual(): boolean {
        if (!this.entitlement?.archiveStorage || !this.information?.deploymentSKU?.archiveStorage) {
            // we have not been deployed
            // we haven't got an active SKU
            // or something has gone terribly wrong
            return true;
        }
        return this.equals(this.entitlement.archiveStorage.quantity, this.information.deploymentSKU.archiveStorage.quantity);
    }

    public get isValid(): boolean {
        return this.entitlement && this.entitlement.isValid;
    }

    public get allocatedEPS(): number {
        if (!this.entitlement?.compute) {
            // we have not been deployed
            // we haven't got an active SKU
            // or something has gone terribly wrong
            return 0;
        }

        return this.entitlement.compute.quantity * 1000;
    }

    private equals(original: number, current: number): boolean {
        return original === current;
    }
}

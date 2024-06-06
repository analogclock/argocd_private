//  Angular imports
import { Injectable } from '@angular/core';
//  Application imports
import { BaseProvisioningService } from './base-provisioning.service';
import { Endpoints } from './endpoints';
//  Third party imports
import { Observable } from 'rxjs';
import { RUpgradeModel } from 'app/models/upgrade-model';
import { RActivation } from 'app/records/activation.record';

@Injectable({
    providedIn: 'root'
})
export class UpgradeService extends BaseProvisioningService {
    public hasUpgradeScheduled(accountId: number,
        serialNumber: string): Observable<Array<RUpgradeModel>> {

        return this.apiGet<RUpgradeModel>(
            `${Endpoints.UPGRADE}/${accountId}/${serialNumber}`,
            RUpgradeModel
        ) as any as Observable<Array<RUpgradeModel>>;
    }

    public addSchedule(accountId: number,
        serialNumber: string, upgrade: RUpgradeModel): Observable<RActivation> {

        return this.apiPost<RUpgradeModel, RActivation>(
            `${Endpoints.UPGRADE}/${accountId}/${serialNumber}`,
            upgrade,
            RActivation
        ) as any as Observable<RActivation>;
    }
}

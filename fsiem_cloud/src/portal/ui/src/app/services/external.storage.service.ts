//  Angular imports
import { Injectable } from '@angular/core';
//  Application imports
import { BaseProvisioningService } from './base-provisioning.service';
import { Endpoints } from './endpoints';
//  Third party imports
import { Observable } from 'rxjs';
import { RActivation } from 'app/records/activation.record';
import { RExternalStorageDetailModel } from 'app/models/external-storage-detail-model';

@Injectable({
    providedIn: 'root'
})
export class ExternalStorageService extends BaseProvisioningService {

    public getExternalStorages(accountId: number,
        serialNumber: string): Observable<Array<RExternalStorageDetailModel>> {
        return this.apiGet<RExternalStorageDetailModel>(
            `${Endpoints.EXTERNAL_STORAGE}/${accountId}/${serialNumber}`,
            RExternalStorageDetailModel
        ) as any as Observable<Array<RExternalStorageDetailModel>>;
    }

    public addStorage(accountId: number, model: RExternalStorageDetailModel): Observable<RActivation> {
        return this.apiPost<RExternalStorageDetailModel, RActivation>(
            `${Endpoints.EXTERNAL_STORAGE}/${accountId}/${model.serialNumber}`,
            model,
            RActivation
        ) as any as Observable<RActivation>;
    }

    public deleteStorage(accountId: number, model: RExternalStorageDetailModel): Observable<RActivation> {
        return this.apiDeleteBody<RExternalStorageDetailModel, RActivation>(
            `${Endpoints.EXTERNAL_STORAGE}/${accountId}/${model.serialNumber}`,
            model,
            RActivation
        ) as any as Observable<RActivation>;
    }
}

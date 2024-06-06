//  Angular imports
import { Injectable } from '@angular/core';
//  Application imports
import { BaseProvisioningService } from './base-provisioning.service';
import { Endpoints } from './endpoints';
//  Third party imports
import { Observable } from 'rxjs';
import { RVersion } from 'app/records/version.record';

@Injectable({
    providedIn: 'root'
})
export class VersionService extends BaseProvisioningService {
    public checkForUpdate(accountId: number,
        serialNumber: string): Observable<Array<RVersion>> {

        return this.apiGet<RVersion>(
            `${Endpoints.VERSION}/${accountId}/${serialNumber}/update`,
            RVersion
        ) as any as Observable<Array<RVersion>>;
    }
}

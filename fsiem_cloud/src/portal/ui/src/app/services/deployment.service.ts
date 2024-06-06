//  Angular imports
import { Injectable } from '@angular/core';
//  Application imports
import { BaseProvisioningService } from './base-provisioning.service';
import { Endpoints } from './endpoints';
import { RActivatedStackInformation } from 'app/records/activated-stack-information.record';
import { RActivation } from 'app/records/activation.record';
import { RDeployment } from 'app/records/deployment.record';
//  Third party imports
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class DeploymentService extends BaseProvisioningService {
    public getDeployments(accountId: number): Observable<Array<RDeployment>> {
        return this.apiGet<RDeployment>(
            `${Endpoints.DEPLOYMENT}/${accountId}`,
            RDeployment
        ) as any as Observable<Array<RDeployment>>;
    }

    public getDeployment(accountId: number, serialNumber: string): Observable<RDeployment> {
        return this.apiGet<RDeployment>(
            `${Endpoints.DEPLOYMENT}/${accountId}/${serialNumber}`,
            RDeployment
        ) as any as Observable<RDeployment>;
    }

    public deleteDeployment(accountId: number, serialNumber: string): Observable<boolean> {
        return this.apiDelete(
            `${Endpoints.DEPLOYMENT}/${accountId}/${serialNumber}`,
        );
    }

    public activate(
        accountId: number,
        serialNumber: string,
        activatedStackInformation: RActivatedStackInformation
    ): Observable<RActivation> {
        return this.apiPut<RActivatedStackInformation, RActivation>(
            `${Endpoints.DEPLOYMENT}/${accountId}/${serialNumber}`,
            activatedStackInformation,
            RActivation
        );
    }

    public update(
        accountId: number,
        serialNumber: string,
        activatedStackInformation: RActivatedStackInformation
    ): Observable<RActivation> {
        return this.apiPost<RActivatedStackInformation, RActivation>(
            `${Endpoints.DEPLOYMENT}/update/${accountId}/${serialNumber}`,
            activatedStackInformation,
            RActivation
        );
    }
}

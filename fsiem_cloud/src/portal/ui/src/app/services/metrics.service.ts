//  Angular imports
import { Injectable } from '@angular/core';
//  Application imports
import { BaseProvisioningService } from './base-provisioning.service';
import { Endpoints } from './endpoints';
//  Third party imports
import { Observable } from 'rxjs';
import { RMetricData } from 'app/records/metric-data.record';
import { RStorageDataRow } from 'app/records/storage-data.record';

@Injectable({
    providedIn: 'root'
})
export class MetricsService extends BaseProvisioningService {
    public getMetrics(accountId: number, serialNumber: string,
        metric: string, time: string): Observable<Array<RMetricData>> {
        return this.apiGet<RMetricData>(
            `${Endpoints.METRICS}/${accountId}/${serialNumber}?metric=${metric}&time=${time}`,
            RMetricData
        ) as any as Observable<Array<RMetricData>>;
    }

    public getStorageMetrics(accountId: number, serialNumber: string): Observable<RStorageDataRow> {
        return this.apiGet<RStorageDataRow>(
            `${Endpoints.METRICS}/storage/${accountId}/${serialNumber}`,
            RStorageDataRow
        ) as any as Observable<RStorageDataRow>;
    }
}

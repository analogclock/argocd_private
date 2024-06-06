//  Angular imports
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { TestBed, TestBedStatic } from '@angular/core/testing';
//  Application imports
import { BaseProvisioningService } from './base-provisioning.service';

describe('BaseProvisioningServiceService', (): void => {
    beforeEach((): TestBedStatic => TestBed.configureTestingModule({
        imports: [ HttpClientTestingModule ]
    }));

    it('should create', (): void => {
        const service: BaseProvisioningService = TestBed.inject(BaseProvisioningService);
        expect(service).toBeTruthy();
    });
});

//  Angular imports
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { TestBed, TestBedStatic } from '@angular/core/testing';
//  Application imports
import { DeploymentService } from './deployment.service';

describe('DeploymentService', (): void => {
    beforeEach((): TestBedStatic => TestBed.configureTestingModule({
        imports: [ HttpClientTestingModule ]
    }));

    it('should create', (): void => {
        const service: DeploymentService = TestBed.inject(DeploymentService);
        expect(service).toBeTruthy();
    });
});

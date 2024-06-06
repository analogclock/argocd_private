//  Angular imports
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { TestBed, TestBedStatic } from '@angular/core/testing';
//  Application imports
import { UserService } from './user.service';

describe('UserService', (): void => {
    beforeEach((): TestBedStatic => TestBed.configureTestingModule({
        imports: [ HttpClientTestingModule ]
    }));

    it('should be created', (): void => {
        const service: UserService = TestBed.inject(UserService);
        expect(service).toBeTruthy();
    });
});

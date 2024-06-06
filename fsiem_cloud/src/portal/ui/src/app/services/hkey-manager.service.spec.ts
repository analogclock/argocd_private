//  Angular imports
import { TestBed, TestBedStatic } from '@angular/core/testing';
//  Application imports
import { HKeyManagerService } from './hkey-manager.service';
//  Third party imports
import { CookieModule } from 'ngx-cookie';

describe('HKeyManagerService', (): void => {
    beforeEach((): TestBedStatic => TestBed.configureTestingModule({
        imports: [ CookieModule.forRoot() ]
    }));

    it('should be created', (): void => {
        const service: HKeyManagerService = TestBed.inject(HKeyManagerService);
        expect(service).toBeTruthy();
    });
});

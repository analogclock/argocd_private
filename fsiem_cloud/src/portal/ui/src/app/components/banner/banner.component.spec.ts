//  Angular imports
import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';
//  Application imports
import { BannerComponent } from './banner.component';
import { RSubMenuItem } from 'app/records/menu-item.record';
import { StorageItem } from 'app/models/storage-item';
import { UserService } from 'app/services/user.service';
import { UserServiceMock } from 'app/services/user.service.mock';
import { WINDOW_TOKEN } from 'app/window-token';
import { WindowMock } from 'app/window-mock';
//  Third party imports
import { CookieModule } from 'ngx-cookie';

describe('BannerComponent', (): void => {
    let component: BannerComponent;
    let fixture: ComponentFixture<BannerComponent>;

    beforeEach(waitForAsync((): void => {
        TestBed.configureTestingModule({
            imports: [
                CookieModule.forRoot()
            ],
            declarations: [ BannerComponent ],
            schemas: [ NO_ERRORS_SCHEMA ],
            providers: [
                { provide: UserService, useClass: UserServiceMock },
                { provide: WINDOW_TOKEN, useClass: WindowMock }
            ]
        }).compileComponents();
    }));

    beforeEach((): void => {
        fixture = TestBed.createComponent(BannerComponent);
        component = fixture.componentInstance;
    });

    it('should create', (): void => {
        // fixture.detectChanges();
        expect(component).toBeTruthy();
    });

    it('should redirect to Fortinet One', (): void => {
        const redirectSpy: jasmine.Spy = spyOnProperty(component['window'].location, 'href', 'set');
        spyOn(component['cookieService'], 'remove');
        component.redirectToFortinetOneLogin();
        expect(component).toBeTruthy();
        expect(component['cookieService'].remove).toHaveBeenCalledWith(StorageItem.AUTH_TOKEN);
        expect(redirectSpy).toHaveBeenCalled();
    });

    it('should set selected portal', (): void => {
        const event: MouseEvent = { preventDefault: (): void => {}, stopPropagation: (): void => {} } as MouseEvent;
        const enabledPortal: RSubMenuItem = { visibility: 'ShowEnabled' } as RSubMenuItem;
        spyOn(event, 'preventDefault');
        spyOn(event, 'stopPropagation');
        component.selectPortal(enabledPortal, event);
        expect(event.stopPropagation).not.toHaveBeenCalled();
        expect(event.preventDefault).not.toHaveBeenCalled();
        expect(component.selectedPortal).toBe(enabledPortal);
        const disabledPortal: RSubMenuItem = { visibility: 'ShowDisabled' } as RSubMenuItem;
        component.selectPortal(disabledPortal, event);
        expect(event.stopPropagation).toHaveBeenCalled();
        expect(event.preventDefault).toHaveBeenCalled();
        expect(component.selectedPortal).toBe(enabledPortal);
    });
});

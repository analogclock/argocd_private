//  Angular imports
import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { RouterTestingModule } from '@angular/router/testing';
//  Application imports
import { AccountSelectionComponent } from './account-selection.component';
import { ApplicationRoute } from 'app/models/application-route';
import { HKeyManagerService } from 'app/services/hkey-manager.service';
import { HKeyManagerServiceMock } from 'app/services/hkey-manager.service.mock';
import { MockComponent } from '../mock.component';
import { RAccount } from 'app/records/account.record';
import { RAccountDetails } from 'app/records/account-details.record';
import { RHKeyData } from 'app/records/h-key-data.record';
import { UserService } from 'app/services/user.service';
import { UserServiceMock } from 'app/services/user.service.mock';
//  Third party imports
import { CookieModule } from 'ngx-cookie';
import { of } from 'rxjs';

const account1: RAccountDetails = {
    accountId: 1,
    accountEmail: 'some@email.com',
    accountCompany: 'Thirtynet',
    masterUserName: 'dude',
    allAssetsAccess: false,
    userId: 2,
    userEmail: 'joe@black.com'
} as RAccountDetails;

const account2: RAccountDetails = {
    accountId: 1,
    accountEmail: 'other@email.com',
    accountCompany: 'Twentynet',
    masterUserName: 'bloke',
    allAssetsAccess: true,
    userId: 3.5,
    userEmail: 'jack@ripper.com'
} as RAccountDetails;

const hKeyData: RHKeyData = new RHKeyData();
hKeyData.accountId = '1';
hKeyData.userId = '2';
hKeyData.userFullAccess = false;

describe('AccountSelectionComponent', (): void => {
    let component: AccountSelectionComponent;
    let fixture: ComponentFixture<AccountSelectionComponent>;

    beforeEach(waitForAsync((): void => {
        TestBed.configureTestingModule({
            imports: [
                RouterTestingModule.withRoutes([
                    { path: ApplicationRoute.ENTITLEMENTS, component: MockComponent }
                ]),
                HttpClientTestingModule,
                CookieModule.forRoot()
            ],
            declarations: [
                AccountSelectionComponent,
                MockComponent
            ],
            schemas: [ NO_ERRORS_SCHEMA ],
            providers: [
                { provide: UserService, useClass: UserServiceMock },
                { provide: HKeyManagerService, useClass: HKeyManagerServiceMock }
            ]
        }).compileComponents();
    }));

    beforeEach((): void => {
        fixture = TestBed.createComponent(AccountSelectionComponent);
        component = fixture.componentInstance;
    });

    it('should create', (): void => {
        spyOn(component as any, 'loadAccounts');
        fixture.detectChanges();
        expect(component).toBeTruthy();
        expect(component['loadAccounts']).toHaveBeenCalled();
    });

    it('should pick account', (): void => {
        const account: RAccount = new RAccount();
        account.details = new RAccountDetails;
        spyOn(component['userService'], 'getAccount').and.returnValue(of(account));
        spyOn(component as any, 'setSelectedAccount');
        component.pickAccount(account1);
        expect(component['userService'].getAccount).toHaveBeenCalledWith(1, 2);
        expect(component['setSelectedAccount']).toHaveBeenCalledWith(account);
    });

    it('should load multiple accounts', (): void => {
        spyOn(component['userService'] as any, 'getAccounts').and.returnValue(of([account1, account2]));
        spyOn(component, 'pickAccount');
        component['loadAccounts']();
        expect(component.accounts).toEqual([account1, account2]);
        expect(component.pickAccount).not.toHaveBeenCalled();
    });


    it('should load single account', (): void => {
        spyOn(component['userService'] as any, 'getAccounts').and.returnValue(of([account1]));
        spyOn(component, 'pickAccount');
        component['loadAccounts']();
        expect(component['userService'].getAccounts).toHaveBeenCalled();
        expect(component.pickAccount).toHaveBeenCalledWith(account1);
    });

    it('should set selected account', (): void => {
        const account: RAccount = new RAccount();
        account.details = new RAccountDetails();
        spyOn(component as any, 'completeAndStore');
        spyOn(component['userService'].accountSelected$, 'next');
        spyOn(component['router'], 'navigateByUrl');
        component['setSelectedAccount'](account);
        expect(component['completeAndStore']).toHaveBeenCalledWith(account.details);
        expect(component['userService'].accountSelected$.next).toHaveBeenCalledOnceWith(account);
        expect(component['router'].navigateByUrl).toHaveBeenCalledWith(ApplicationRoute.ENTITLEMENTS);
    });
});

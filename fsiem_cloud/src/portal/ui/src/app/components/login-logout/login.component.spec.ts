//  Angular imports
import { ActivatedRoute } from '@angular/router';
import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { RouterTestingModule } from '@angular/router/testing';
//  Application imports
import { ApplicationRoute } from 'app/models/application-route';
import { AuthToken } from 'app/models/auth-token';
import { HKeyManagerService } from 'app/services/hkey-manager.service';
import { HKeyManagerServiceMock } from 'app/services/hkey-manager.service.mock';
import { LoginComponent } from './login.component';
import { MockComponent } from '../mock.component';
import { RHKeyData } from 'app/records/h-key-data.record';
import { StorageItem } from 'app/models/storage-item';
import { UserService } from 'app/services/user.service';
import { UserServiceMock } from 'app/services/user.service.mock';
//  Third party imports
import { CookieModule } from 'ngx-cookie';
import { of } from 'rxjs';

const fragment: string = 'access_token=123&token_type=Bearer&expires_in=3600';

describe('LoginComponent', (): void => {
    let component: LoginComponent;
    let fixture: ComponentFixture<LoginComponent>;

    beforeEach(waitForAsync((): void => {
        TestBed.configureTestingModule({
            imports: [
                HttpClientTestingModule,
                RouterTestingModule.withRoutes([
                    { path: ApplicationRoute.ENTITLEMENTS, component: MockComponent },
                    { path: ApplicationRoute.ACCOUNT_SELECTION, component: MockComponent }
                ]),
                CookieModule.forRoot()
            ],
            declarations: [
                LoginComponent,
                MockComponent
            ],
            schemas: [ NO_ERRORS_SCHEMA ],
            providers: [
                {
                    provide: ActivatedRoute, useValue: {
                        fragment: of(fragment)
                    }
                },
                { provide: UserService, useClass: UserServiceMock },
                { provide: HKeyManagerService, useClass: HKeyManagerServiceMock }
            ]
        }).compileComponents();
    }));

    beforeEach((): void => {
        fixture = TestBed.createComponent(LoginComponent);
        component = fixture.componentInstance;
    });

    it('should create', (): void => {
        component['route'] = { fragment: of('token_type=fake&expires_in=0') } as any as ActivatedRoute;
        const authToken: AuthToken = new AuthToken();
        authToken.data = 'data';
        spyOn(component as any, 'parseFragment').and.returnValue(authToken);
        spyOn(component['userService'], 'setAuthenticated');
        spyOn(component['userService'], 'getAccount').and.returnValue(of(null));
        spyOn(RHKeyData, 'fromBase64Encoded').and.returnValue({ accountId: '1', userId: '2' } as RHKeyData);
        fixture.detectChanges();
        expect(component).toBeTruthy();
        expect(component['parseFragment']).toHaveBeenCalledWith('token_type=fake&expires_in=0');
        expect(component['userService'].setAuthenticated).toHaveBeenCalled();
        expect(RHKeyData.fromBase64Encoded).toHaveBeenCalled();
        expect(component['userService'].getAccount).toHaveBeenCalledWith(1, 2);
    });

    it('should parse fragments', (): void => {
        spyOn(component['cookieService'], 'putObject');
        component['parseFragment'](fragment);
        expect(component['cookieService'].putObject).toHaveBeenCalledWith(
            StorageItem.AUTH_TOKEN,
            AuthToken.fromString(fragment.split('&')),
            jasmine.anything()
        );
    });
});

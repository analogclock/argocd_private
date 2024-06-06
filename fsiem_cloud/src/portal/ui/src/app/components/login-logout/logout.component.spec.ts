//  Angular imports
import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
//  Application imports
import { LogoutComponent } from './logout.component';
import { MockComponent } from '../mock.component';
import { StorageItem } from 'app/models/storage-item';
import { UserService } from 'app/services/user.service';
import { UserServiceMock } from 'app/services/user.service.mock';
import { WINDOW_TOKEN } from 'app/window-token';
import { WindowMock } from 'app/window-mock';
//  Third party imports
import { CookieModule } from 'ngx-cookie';

describe('LogoutComponent', (): void => {
    let component: LogoutComponent;
    let fixture: ComponentFixture<LogoutComponent>;

    beforeEach(waitForAsync((): void => {
        TestBed.configureTestingModule({
            imports: [
                CookieModule.forRoot()
            ],
            declarations: [
                LogoutComponent,
                MockComponent
            ],
            providers: [
                { provide: UserService, useClass: UserServiceMock },
                { provide: WINDOW_TOKEN, useClass: WindowMock }
            ]
        }).compileComponents();
    }));

    beforeEach((): void => {
        fixture = TestBed.createComponent(LogoutComponent);
        component = fixture.componentInstance;
    });

    it('should create', (): void => {
        spyOn(component['userService'], 'clearAuthenticated');
        spyOn(component['cookieService'], 'remove');
        const redirectSpy: jasmine.Spy = spyOnProperty(component['window'].location, 'href', 'set');
        expect(component).toBeTruthy();
        fixture.detectChanges();
        expect(component['userService'].clearAuthenticated).toHaveBeenCalled();
        expect(component['cookieService'].remove).toHaveBeenCalledWith(StorageItem.AUTH_TOKEN);
        expect(redirectSpy).toHaveBeenCalled();
    });
});

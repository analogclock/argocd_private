//  Angular imports
import { inject, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
//  Application imports
import { ApplicationRoute } from 'app/models/application-route';
import { AuthenticationGuard } from './authentication.guard';
import { MockComponent } from 'app/components/mock.component';
import { UserService } from 'app/services/user.service';
import { UserServiceMock } from 'app/services/user.service.mock';
//  Third party imports
import { Observable } from 'rxjs';

describe('AuthenticationGuard', (): void => {
    let guard: AuthenticationGuard;

    beforeEach((): void => {
        TestBed.configureTestingModule({
            imports: [
                RouterTestingModule.withRoutes([
                    { path: ApplicationRoute.SPLASH, component: MockComponent }
                ])
            ],
            declarations: [ MockComponent ],
            providers: [
                AuthenticationGuard,
                { provide: UserService, useClass: UserServiceMock }
            ]
        });
    });

    beforeEach(inject([AuthenticationGuard], (_guard: AuthenticationGuard): void => {
        guard = _guard;
    }));

    it('should create', (): void => {
        expect(guard).toBeTruthy();
    });

    it('should not grant access to unauthenticated user', (): void => {
        spyOn(guard['router'], 'navigateByUrl');
        (guard.canActivate() as Observable<boolean>)
            .subscribe(
                (access: boolean): void => {
                    expect(access).toBeFalsy();
                    expect(guard['router'].navigateByUrl).toHaveBeenCalledWith(ApplicationRoute.SPLASH);
                }
            );
    });

    it('should grant access to authenticated user', (): void => {
        const userService: UserServiceMock = new UserServiceMock();
        userService['isAuthenticated'] = true;
        guard['userService'] = userService as any as UserService;

        (guard.canActivate() as Observable<boolean>)
            .subscribe(
                (access: boolean): void => expect(access).toBeTruthy()
            );
    });
});

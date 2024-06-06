//  Angular imports
import { HttpEvent, HttpHandler, HttpRequest, HttpResponse } from '@angular/common/http';
import { TestBed, waitForAsync } from '@angular/core/testing';
//  Application imports
import { AuthInterceptor } from './auth.interceptor';
import { AuthToken } from 'app/models/auth-token';
import { Endpoints } from 'app/services/endpoints';
import { environment } from 'environments/environment';
import { WINDOW_TOKEN } from 'app/window-token';
import { WindowMock } from 'app/window-mock';
//  Third party imports
import { CookieService, ICookieService } from 'ngx-cookie';
import { Observable, of } from 'rxjs';

let token: AuthToken;

export class HttpHandlerMock implements HttpHandler {
    public handle = (_: HttpRequest<any>): Observable<HttpEvent<any>> => of();
}

export class CookieServiceMock implements Partial<ICookieService> {
    public getObject(): any {
        return token;
    }
}

describe('AuthInterceptor', (): void => {
    beforeEach((): void => {
        token = new AuthToken();
        token.tokenType = 'Grinder';
        token.token = 'blablabla...';

        TestBed.configureTestingModule({
            providers: [
                { provide: CookieService, useClass: CookieServiceMock },
                { provide: WINDOW_TOKEN, useClass: WindowMock }
            ]
        });
    });

    it('should be created', (): void => {
        const interceptor: AuthInterceptor = TestBed.inject(AuthInterceptor);
        expect(interceptor).toBeTruthy();
    });

    it('should add authorisation header when both token is present and provisioning api is called', (): void => {
        const interceptor: AuthInterceptor = TestBed.inject(AuthInterceptor);
        const request: HttpRequest<any> = new HttpRequest('GET', environment.provisioningApi + '/some-call');
        const next: HttpHandler = new HttpHandlerMock();
        spyOn(next, 'handle');
        spyOn(interceptor as any, 'handleResponse').and.callFake((a: any): any => a);
        interceptor.intercept(request, next);

        expect(next.handle).toHaveBeenCalledWith(request.clone({
            headers: request.headers.append('Authorization', `${token.tokenType} ${token.token}`)
        }));
    });

    it('should not change request when token is not present', (): void => {
        const interceptor: AuthInterceptor = TestBed.inject(AuthInterceptor);
        const request: HttpRequest<any> = new HttpRequest('GET', environment.provisioningApi + '/some-call');
        const next: HttpHandler = new HttpHandlerMock();
        token = undefined;
        spyOn(next, 'handle');
        spyOn(interceptor as any, 'handleResponse').and.callFake((a: any): any => a);
        interceptor.intercept(request, next);

        expect(next.handle).toHaveBeenCalledWith(request);
    });

    it('should not change request when not provisioning api is called', (): void => {
        const interceptor: AuthInterceptor = TestBed.inject(AuthInterceptor);
        const request: HttpRequest<any> = new HttpRequest('GET', 'bogus-api/some-call');
        const next: HttpHandler = new HttpHandlerMock();
        spyOn(next, 'handle');
        spyOn(interceptor as any, 'handleResponse').and.callFake((a: any): any => a);
        interceptor.intercept(request, next);

        expect(next.handle).toHaveBeenCalledWith(request);
    });

    it('should not handle response from non-user endpoints', (): void => {
        const request: HttpRequest<any> = { url: `${Endpoints.PORTAL_LIST}` } as HttpRequest<any>;
        const response: HttpEvent<any> = new HttpResponse<any>({
            body: { details: { userAuthenticationPassed: false, userAuthenticationUrl: 'some-url'} }
        });
        const interceptor: AuthInterceptor = TestBed.inject(AuthInterceptor);
        const redirectSpy: jasmine.Spy = spyOnProperty(interceptor['window'].location, 'href', 'set');
        interceptor['handleResponse'](request, of(response))
            .subscribe(
                (): void => expect(redirectSpy).not.toHaveBeenCalled()
            );
    });

    it('should not handle response without user details', (): void => {
        const request: HttpRequest<any> = { url: `${Endpoints.USER}` } as HttpRequest<any>;
        const response: HttpEvent<any> = new HttpResponse<any>({
            body: { details: null }
        });
        const interceptor: AuthInterceptor = TestBed.inject(AuthInterceptor);
        const redirectSpy: jasmine.Spy = spyOnProperty(interceptor['window'].location, 'href', 'set');
        interceptor['handleResponse'](request, of(response))
            .subscribe(
                (): void => expect(redirectSpy).not.toHaveBeenCalled()
            );
    });

    it('should not handle response when authentication passed', (): void => {
        const request: HttpRequest<any> = { url: `${Endpoints.USER}` } as HttpRequest<any>;
        const response: HttpEvent<any> = new HttpResponse<any>({
            body: { details: { userAuthenticationPassed: true, userAuthenticationUrl: 'some-url'} }
        });
        const interceptor: AuthInterceptor = TestBed.inject(AuthInterceptor);
        const redirectSpy: jasmine.Spy = spyOnProperty(interceptor['window'].location, 'href', 'set');
        interceptor['handleResponse'](request, of(response))
            .subscribe(
                (): void => expect(redirectSpy).not.toHaveBeenCalled()
            );
    });

    it('should throw error when authentication url is not passed', waitForAsync((): void => {
        const request: HttpRequest<any> = { url: `${Endpoints.USER}` } as HttpRequest<any>;
        const response: HttpEvent<any> = new HttpResponse<any>({
            body: { details: { userAuthenticationPassed: false, userAuthenticationUrl: ''} }
        });
        const interceptor: AuthInterceptor = TestBed.inject(AuthInterceptor);
        interceptor['handleResponse'](request, of(response)).subscribe(
            (): void => {},
            (error: any): void => expect(error.toString()).toContain('User authentication URL not found')
        );
    }));

    it('should handle response', (): void => {
        const request: HttpRequest<any> = { url: `${Endpoints.USER}` } as HttpRequest<any>;
        const response: HttpEvent<any> = new HttpResponse<any>({
            body: { details: { userAuthenticationPassed: false, userAuthenticationUrl: 'some-url'} }
        });
        const interceptor: AuthInterceptor = TestBed.inject(AuthInterceptor);
        const redirectSpy: jasmine.Spy = spyOnProperty(interceptor['window'].location, 'href', 'set');
        interceptor['handleResponse'](request, of(response))
            .subscribe(
                (): void => expect(redirectSpy).toHaveBeenCalledWith('some-url')
            );
    });
});

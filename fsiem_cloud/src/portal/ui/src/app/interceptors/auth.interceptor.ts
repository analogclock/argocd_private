//  Angular imports
import { HttpErrorResponse, HttpEvent, HttpHandler, HttpInterceptor, HttpRequest, HttpResponse } from '@angular/common/http';
import { Inject, Injectable } from '@angular/core';
//  Application imports
import { Endpoints } from 'app/services/endpoints';
import { RAccountDetails } from 'app/records/account-details.record';
import { WINDOW_TOKEN } from 'app/window-token';
//  Third party imports
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { Router } from '@angular/router';
import { ApplicationRoute } from 'app/models/application-route';
import { OidcSecurityService } from 'angular-auth-oidc-client';

@Injectable({
    providedIn: 'root'
})
export class InternalAuthInterceptor implements HttpInterceptor {
    constructor(
        private router: Router,
        private oidc: OidcSecurityService,
        @Inject(WINDOW_TOKEN)
        private window: Window
    ) { }

    public intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
        return this.handleResponse(request, next.handle(request));
    }

    private handleResponse(request: HttpRequest<any>, response: Observable<HttpEvent<any>>): Observable<HttpEvent<any>> {
        return response.pipe(
            tap(
                (event: HttpEvent<any>): void => {
                    if (request.url.indexOf(Endpoints.USER) > -1 && event instanceof HttpResponse && !!event.body && !!event.body.details) {
                        const details: RAccountDetails = event.body.details;
                        // if user authentication fails
                        if (!details.userAuthenticationPassed) {
                            // fail if no url has been given for user authentication
                            if (!details.userAuthenticationUrl) {
                                throw new Error('User authentication URL not found.');
                            // or redirect to the given url
                            } else {
                                this.window.location.href = details.userAuthenticationUrl;
                            }
                        }
                    }
                },
                (err: any) => {
                    if (err instanceof HttpErrorResponse) {
                        if (err.status === 401) {
                            // retry and authorize
                            this.oidc.authorize();
                        }
                    }
                }
            )
        );
    }
}

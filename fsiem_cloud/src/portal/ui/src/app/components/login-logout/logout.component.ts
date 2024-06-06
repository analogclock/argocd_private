//  Angular imports
import { Component, Inject, OnInit } from '@angular/core';
//  Application imports
import { environment } from 'environments/environment';
import { StorageItem } from 'app/models/storage-item';
import { UserService } from 'app/services/user.service';
import { WINDOW_TOKEN } from 'app/window-token';
//  Third party imports
import { CookieService } from 'ngx-cookie';
import { ActivatedRoute, Router } from '@angular/router';
import { ApplicationRoute } from 'app/models/application-route';
import { OidcSecurityService } from 'angular-auth-oidc-client';

@Component({
    selector: 'zf-logout',
    template: ''
})
export class LogoutComponent implements OnInit {
    constructor(
        private userService: UserService,
        private cookieService: CookieService,
        private route: ActivatedRoute,
        private oidc: OidcSecurityService,
        private router: Router,
        @Inject(WINDOW_TOKEN)
        private window: Window
    ) { }

    public ngOnInit(): void {
        // We must maintain a unified logout route
        // which our portal, and the IDP, can reach.

        // We must always clear our authentication
        // regardless of the scenario (us, or IDP)
        this.userService.clearAuthenticated();
        this.cookieService.remove(StorageItem.AUTH_TOKEN);

        if (!this.route.snapshot.queryParamMap.has('SAMLResponse')) {
            // We do not have SAMLResponse returned from IDP
            // This means we have clicked logout from our portal
            // so first hit our SP, which will redirect
            // to IDP for logout for others
            this.oidc.logoffLocal();
            this.window.location.href =
                `${environment.cognitoUrl}/logout?client_id=${environment.clientId}&redirect_uri=${window.location.host}`;
            return;
        }

        // When we have a SAMLResponse in the query parameters (i.e /logout?SAMLResponse=...)
        // we have returned from the IDP, and should redirect our users to the splash screen
        this.router.navigateByUrl(ApplicationRoute.SPLASH);
    }
}

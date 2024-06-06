//  Angular imports
import { Component, Inject, HostBinding, OnInit } from '@angular/core';
import { environment } from 'environments/environment';
import { WINDOW_TOKEN } from 'app/window-token';
import { LoginResponse, OidcSecurityService } from 'angular-auth-oidc-client';

@Component({
    selector: 'zf-splash',
    templateUrl: './splash.component.html',
    styleUrls: ['./splash.component.scss']
})
export class SplashComponent implements OnInit {

    // add the specified class to the entire component
    // allows us to display only the product-information
    // at full height
    @HostBinding('class') public class = 'full-height';

    public readonly productName: string = environment.productName;

    constructor(
        private oidcSecurityService: OidcSecurityService,
        @Inject(WINDOW_TOKEN)
        private window: Window) { }

    public ngOnInit(): void {
        this.oidcSecurityService.checkAuth().subscribe((login: LoginResponse) => {
            if(login.isAuthenticated) {
                // re auth to make sure
                // also runs through the entire auth cycle
                this.oidcSecurityService.authorize();
            }
        });
    }

    public redirectToLogin(): void {
        this.oidcSecurityService.authorize();
    }

    public redirectToRegister(): void {
        this.window.location.href = environment.registerUrl;
    }
}

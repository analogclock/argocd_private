//  Angular imports
import { ActivatedRoute, Router } from '@angular/router';
import { AfterViewInit, Component } from '@angular/core';
//  Application imports
import { ApplicationRoute } from 'app/models/application-route';
import { HKeyManagerService } from 'app/services/hkey-manager.service';
import { RAccount } from 'app/records/account.record';
import { RHKeyData } from 'app/records/h-key-data.record';
import { UserService } from 'app/services/user.service';
//  Third party imports
import { jwtDecode } from 'jwt-decode';
import { LoginResponse, OidcSecurityService } from 'angular-auth-oidc-client';

@Component({
    selector: 'zf-login',
    template: '<div style="width:100%; height: calc(100vh - 102px);"></div><zf-loading-indicator></zf-loading-indicator>'
})
export class LoginComponent implements AfterViewInit {

    constructor(
        private router: Router,
        private route: ActivatedRoute,
        private oidcSecurityService: OidcSecurityService,
        private userService: UserService,
        private hKeyManagerService: HKeyManagerService
    ) { }

    public ngAfterViewInit(): void {
        // check, and subscribe
        // to changes on the authentication state
        this.oidcSecurityService
            .checkAuth()
            .subscribe((loginRes: LoginResponse) => {

                if (!loginRes.isAuthenticated) {
                    // eslint-disable-next-line no-console
                    console.error('we are unauthenticated');
                    this.userService.clearAuthenticated();
                    this.router.navigateByUrl(ApplicationRoute.SPLASH);
                    return;
                }

                const data = this.route.snapshot.queryParamMap.get('data');
                // const authToken: AuthToken = this.parseFragmentFromToken(token);
                const decoded: any = jwtDecode(loginRes.idToken);
                // do we have an IAM username, if not resolve the userId
                let userId = decoded['custom:IAM_username'] ?? '';
                if (userId === '') {
                    userId = decoded['identities'][0]['userId'];
                    // if we don't have an '@' we're a fortinet address
                    // but we don't get that back from the token
                    // so we need to add it in
                    userId = userId.indexOf('@') === -1 ? `${userId}@fortinet.com` : userId;
                }
                this.userService.setAuthenticated();
                this.userService.setGlobalUserId(userId);

                // we have no previous login details
                // i.e we have not come from another portal
                if (!data || data === '') {
                    // we need to load up the accounts
                    // do we have hkeydata?
                    // if we do we can use it to determine our last account

                    const hKeyData: RHKeyData = this.hKeyManagerService.get() ?? null;
                    if (hKeyData !== null) {
                        this.userService.getAccount(
                            parseInt(hKeyData.accountId, 10),
                            parseInt(hKeyData.userId, 10)
                        ).subscribe((account: RAccount): void => {
                            this.userService.accountSelected$.next(account);
                            this.router.navigateByUrl(ApplicationRoute.ACCOUNT_SELECTION);
                        });
                    } else {
                        this.router.navigateByUrl(ApplicationRoute.ACCOUNT_SELECTION);
                    }
                } else {
                    const hKeyData: RHKeyData = RHKeyData.fromBase64Encoded(data);
                    // an explicit check for null
                    if (hKeyData !== null) {
                        this.hKeyManagerService.store(hKeyData);
                        this.userService.getAccount(
                            parseInt(hKeyData.accountId, 10),
                            parseInt(hKeyData.userId, 10)
                        ).subscribe((account: RAccount): void => {
                            this.userService.accountSelected$.next(account);
                            this.router.navigateByUrl(ApplicationRoute.ACCOUNT_SELECTION);
                        });
                    }
                }
            });
    }
}

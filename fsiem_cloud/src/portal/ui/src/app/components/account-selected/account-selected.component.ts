//  Angular imports
import { ActivatedRoute, ParamMap } from '@angular/router';
import { Component, Inject, OnInit } from '@angular/core';
//  Application imports
import { WINDOW_TOKEN } from 'app/window-token';
//  Third party imports
import { RAccount } from 'app/records/account.record';
import { OidcSecurityService, OpenIdConfigLoader, OpenIdConfiguration } from 'angular-auth-oidc-client';

@Component({
    selector: 'zf-account-selected',
    template: ''
})
export class AccountSelectedComponent implements OnInit {

    public accounts: Array<RAccount>;
    public showAccountSelection: boolean = false;
    public showSuperUserInfo: boolean = false;
    public showPartialCreatedAccountInfo: boolean = false;

    constructor(
        private route: ActivatedRoute,
        private oidc: OidcSecurityService,
        @Inject(WINDOW_TOKEN)
        private window: Window
    ) { }

    public ngOnInit(): void {
        const data = this.route.snapshot.queryParamMap.get('data');
        this.oidc.getConfiguration().subscribe((config: OpenIdConfiguration) => {
            this.oidc.authorize(config.configId, {
                customParams: {
                    'state': data
                }
            });
        });
    }
}

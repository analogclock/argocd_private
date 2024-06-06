//  Angular imports
import { AfterViewInit, Component, ElementRef, Inject, OnDestroy, ViewChild } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';
import { Router } from '@angular/router';
//  Application imports
import { environment } from 'environments/environment';
import { ApplicationRoute } from 'app/models/application-route';
import { HKeyManagerService } from 'app/services/hkey-manager.service';
import { RAccount } from 'app/records/account.record';
import { RAccountDetails } from 'app/records/account-details.record';
import { RHKeyData } from 'app/records/h-key-data.record';
import { RMenuItem, RSubMenuItem } from 'app/records/menu-item.record';
import { StorageItem } from 'app/models/storage-item';
import { UserService } from 'app/services/user.service';
import { WINDOW_TOKEN } from 'app/window-token';
//  Third party imports
import { combineLatest, fromEvent, Subscription } from 'rxjs';
import { CookieService } from 'ngx-cookie';
import { takeWhile } from 'rxjs/operators';

@Component({
    selector: 'zf-banner',
    templateUrl: './banner.component.html',
    styleUrls: ['./banner.component.scss']
})
export class BannerComponent implements AfterViewInit, OnDestroy {

    public get registerUrl(): string {
        return environment.registerUrl;
    }

    public get fortifiedHKeyData(): string {
        return JSON.stringify(RHKeyData.toFortinet(this.hKeyData));
    }

    public isAuthenticated: boolean = false;
    public userId: string = null;

    public selectedPortal: RSubMenuItem|RMenuItem = null;
    public open: HTMLDivElement;

    private get hKeyData(): RHKeyData {
        return this.hKeyManagerService.get();
    }

    @ViewChild('services', { static: false })
    private services: ElementRef<HTMLDivElement>;

    @ViewChild('support', { static: false })
    private support: ElementRef<HTMLDivElement>;

    @ViewChild('user', { static: false })
    private user: ElementRef<HTMLDivElement>;

    private account: RAccountDetails;
    private subscriptions: Array<Subscription> = [];

    constructor(
        public userService: UserService,
        public sanitizer: DomSanitizer,
        private cookieService: CookieService,
        private hKeyManagerService: HKeyManagerService,
        @Inject(WINDOW_TOKEN)
        private window: Window,
        private router: Router,
    ) { }

    public ngAfterViewInit(): void {
        this.subscriptions.push(
            combineLatest([
                this.userService.accountSelected$,
                this.userService.isAuthenticated$,
                this.userService.userId$
            ])
                .subscribe(
                    ([account, authenticated, userId]: [RAccount, boolean, string]): void => {
                        this.isAuthenticated = authenticated;
                        if (userId) {
                            this.userId = userId;
                        }
                        if (account?.details) {
                            this.account = account.details;
                        }
                    }
                )
        );
    }

    public selectPortal(portalMenuItem: RSubMenuItem, event: MouseEvent): void {
        if (portalMenuItem.visibility === 'ShowDisabled') {
            event.stopPropagation();
            event.preventDefault();
            return;
        }

        this.selectedPortal = portalMenuItem;
    }

    public onSubmit(e: Event): void {
        if (this.selectedPortal == null || this.selectedPortal.displayName === environment.productName) {
            return;
        }
        const portal: RSubMenuItem|RMenuItem = this.selectedPortal;
        let action: string = '';
        const isNewTab: boolean = true;
        if (portal.displayName.toLowerCase() === 'logout') {
            this.cookieService.remove(StorageItem.AUTH_TOKEN);
            this.hKeyManagerService.delete();
            this.router.navigateByUrl(ApplicationRoute.LOGOUT);
        } else if (portal.displayName.toLowerCase() === 'fortinethome') {
            // very specific use case for FortinetHome
            // they currently do not allow POSTing data to their site
            // so to ensure that we do not look foolish
            // we stop here, and update the location href
            window.location.href = portal.url;
            return;
        } else if (portal.displayName.toLowerCase() === 'switch accounts') {
            // we will re-route to account selection
            this.hKeyManagerService.delete();
            this.userService.accountSelected$.next(null);
            this.router.navigateByUrl(ApplicationRoute.ACCOUNT_SELECTION);
        } else if (!!this.hKeyData && this.hKeyData.hasLastVisited(portal.displayName)) {
            action = this.hKeyData.getLastVisited(portal.displayName);
        } else if (
            !this.account ||
            this.account.allAssetsAccess === null ||
            this.account.allAssetsAccess
        ) {
            action = portal.url;
        } else if (portal.visibility === undefined || portal.visibility === 'ShowEnabled') {
            // sub-user
            // they do not have all access enabled
            // each portal is enabled/disabled by an admin
            // this also covers IAM user too
            action = portal.url;
        }

        if (action !== '') {
            (e.target as HTMLFormElement).action = action;
            (e.target as HTMLFormElement).target = isNewTab ? '_blank' : '';
            (e.target as HTMLFormElement).submit();
        }
    }

    public ngOnDestroy(): void {
        if (!!this.subscriptions) {
            this.subscriptions.forEach(
                (subscription: Subscription): void => subscription.unsubscribe()
            );
        }
    }

    public defaultLogout() {
        const logOut = new RSubMenuItem();
        logOut.displayName = 'Logout';
        logOut.url = environment.logoutUrl;
        this.selectedPortal = logOut;
    }

    public forceUserDropdown() {
        this.toggleDropdown(this.user);
    }

    public forceServices() {
        this.toggleDropdown(this.services);
    }

    public forceSupport() {
        this.toggleDropdown(this.support);
    }

    private toggleDropdown(menu: ElementRef<HTMLDivElement>): void {
        if (this.open === menu.nativeElement) {
            this.open = null;
        } else {
            this.open = menu.nativeElement;
            this.subscriptions.push(
                fromEvent(document, 'click')
                    .pipe(
                        takeWhile((): boolean => this.open === menu.nativeElement)
                    ).subscribe(
                        (event: MouseEvent): void => {
                            if (!menu.nativeElement.contains(event.target as HTMLElement)) {
                                this.open = null;
                            }
                        }
                    )
            );
        }
    }
}

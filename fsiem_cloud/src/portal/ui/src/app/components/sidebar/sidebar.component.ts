//  Angular imports
import { AfterViewInit, Component, Input } from '@angular/core';
import { Router } from '@angular/router';
import { ApplicationRoute } from 'app/models/application-route';
import { UserService } from 'app/services/user.service';
import versionJson from '../../../../version.json';

@Component({
    selector: 'zf-sidebar',
    templateUrl: './sidebar.component.html',
    styleUrls: ['./sidebar.component.scss']
})
export class SidebarComponent implements AfterViewInit {
    public version: string = versionJson.version;
    public fullVersion: string = versionJson.fullVersion;

    public userId: string = null;

    @Input()
    public serialNumber: string = '';

    public readonly route: typeof ApplicationRoute = ApplicationRoute;

    public get isAccountSelection(): boolean {
        return this.hasRoute(ApplicationRoute.ACCOUNT_SELECTION);
    }

    public get isEntitlements(): boolean {
        return this.hasRoute(ApplicationRoute.ENTITLEMENTS);
    }

    constructor(
        public router: Router,
        public userService: UserService
    ) { }

    public ngAfterViewInit(): void {
        this.userService.userId$.subscribe((user: string) => {
            this.userId = user;
        });
    }

    public navigateEntitlements(): void {
        this.router.navigateByUrl(ApplicationRoute.ENTITLEMENTS);
    }

    private hasRoute(route: ApplicationRoute): boolean {
        return this.router.url.includes(route);
    }
}

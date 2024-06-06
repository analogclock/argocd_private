//  Angular imports
import { AfterViewInit, Component, OnDestroy } from '@angular/core';
//  Application imports

import { UserService } from 'app/services/user.service';

import { combineLatest, Subscription } from 'rxjs';

@Component({
    selector: 'zf-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss']
})
export class AppComponent implements AfterViewInit, OnDestroy {

    public currentYear: number = new Date().getFullYear();

    public isAuthenticated: boolean = false;
    private subscriptions: Array<Subscription> = [];

    constructor(public userService: UserService) { }

    /*
    After we have initialized the view.
    We will check whether we are truly
    authenticated with the backend
    */
    public ngAfterViewInit(): void {
        this.subscriptions.push(
            combineLatest([
                this.userService.isAuthenticated$
            ])
                .subscribe(
                    ([authenticated]: [boolean]): void => {
                        this.isAuthenticated = authenticated;
                    }
                )
        );
    }

    public ngOnDestroy(): void {
        if (!!this.subscriptions) {
            this.subscriptions.forEach(
                (subscription: Subscription): void => subscription.unsubscribe()
            );
        }
    }
}

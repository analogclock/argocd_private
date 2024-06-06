//  Angular imports
import { CanActivate, Router } from '@angular/router';
import { Injectable } from '@angular/core';
//  Application imports
import { ApplicationRoute } from 'app/models/application-route';
import { UserService } from 'app/services/user.service';
//  Third party imports
import { first, tap } from 'rxjs/operators';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class AuthenticationGuard implements CanActivate {

    constructor(
        private router: Router,
        private userService: UserService
    ) { }

    public canActivate (): Observable<boolean> | Promise<boolean> | boolean {
        return this.userService.isAuthenticated$
            .pipe(
                first(),
                tap(
                    (isAuthenticated: boolean): void => {
                        if (!isAuthenticated) {
                            this.router.navigateByUrl(ApplicationRoute.SPLASH);
                        }
                    }
                )
            );
    }
}

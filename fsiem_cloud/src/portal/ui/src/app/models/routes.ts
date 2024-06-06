//  Angular imports
import { Routes } from '@angular/router';
//  Application imports
import { AccountSelectedComponent } from 'app/components/account-selected/account-selected.component';
import { AccountSelectionComponent } from 'app/components/account-selection/account-selection.component';
import { ApplicationRoute } from './application-route';
import { AuthenticationGuard } from '../guards/authentication.guard';
import { DeploymentDetailsComponent } from 'app/components/deployment-details/deployment-details.component';
import { DeploymentsTableComponent } from '../components/deployment/deployments-table.component';
import { LoginComponent } from '../components/login-logout/login.component';
import { LogoutComponent } from '../components/login-logout/logout.component';
import { ProductInformationComponent } from '../components/product-info/product-information.component';
import { SplashComponent } from 'app/components/splash/splash.component';

export const routes: Routes = [
    { path: ApplicationRoute.NULL, redirectTo: ApplicationRoute.SPLASH, pathMatch: 'full' },
    // AUTHENTICATED ROUTES
    { path: ApplicationRoute.NULL, canActivate: [ AuthenticationGuard ], children: [
        { path: ApplicationRoute.ACCOUNT_SELECTION, component: AccountSelectionComponent },
        { path: ApplicationRoute.PRODUCT_INFORMATION, component: ProductInformationComponent },
        { path: ApplicationRoute.ENTITLEMENTS, children: [
            { path: '', component: DeploymentsTableComponent, pathMatch: 'full' },
            { path: ':serial', component: DeploymentDetailsComponent }
        ] }
    ] },
    // UNAUTHENTICATED ROUTES
    { path: ApplicationRoute.ACCOUNT_SELECTED, component: AccountSelectedComponent },
    { path: ApplicationRoute.LOGIN, component: LoginComponent },
    { path: ApplicationRoute.LOGOUT, component: LogoutComponent },
    { path: ApplicationRoute.SPLASH, component: SplashComponent },
    { path: '**', redirectTo: ApplicationRoute.SPLASH }
];

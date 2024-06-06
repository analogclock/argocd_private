//  Angular imports
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';
import { RouterModule } from '@angular/router';
//  Application imports
import { AccountSelectedComponent } from './components/account-selected/account-selected.component';
import { AccountSelectionComponent } from './components/account-selection/account-selection.component';
import { SidebarComponent } from './components/sidebar/sidebar.component';
import { AppComponent } from './components/app/app.component';
import { InternalAuthInterceptor } from './interceptors/auth.interceptor';
import { BannerComponent } from './components/banner/banner.component';
import { DeploymentDetailsComponent } from './components/deployment-details/deployment-details.component';
import { DeploymentsTableComponent } from './components/deployment/deployments-table.component';
import { LoadingIndicatorComponent } from './components/loading-indicator/loading-indicator.component';
import { LoginComponent } from './components/login-logout/login.component';
import { LogoutComponent } from './components/login-logout/logout.component';
import { ProductInformationComponent } from './components/product-info/product-information.component';
import { routes } from './models/routes';
import { WINDOW_TOKEN } from './window-token';
import { windowProvider } from './window-provider';
import { ZFDropdownModule } from './dropdown-module/zf-dropdown.module';
import { ZFModalModule } from './modal-module';
//  Third party imports
import { CookieModule, CookieService } from 'ngx-cookie';
import { CsvDisplayPipe } from './pipes/csv-display.pipe';
import { UrlDisplayPipe } from './pipes/url-display.pipe';
import { UpgradeDatePipe } from './pipes/upgrade-date-pipe';
import { DeploymentTypePipe } from './pipes/deployment-type.pipe';
import { PascalToHumanPipe } from './pipes/pascal-to-human.pipe';
import { SKUDisplayPipe } from './pipes/sku-display.pipe';
import { ErrorDisplayTextPipe } from './pipes/error-display.pipe';
import { OrgIdPipe } from './pipes/orgId.pipe';
import { NgxChartsModule } from '@swimlane/ngx-charts';
import { DiskSizePipe } from './pipes/disk-size.pipe';
import { ScheduledUpgradeComponent } from './components/schedule-upgrade/schedule-upgrade.component';
import { AuthModule, LogLevel, AuthInterceptor } from 'angular-auth-oidc-client';
import { environment } from 'environments/environment';
import { ApplicationRoute } from './models/application-route';
import { VerticalBarWidgetComponent } from './components/widgets/vertical-bar-widget.component';

@NgModule({
    declarations: [
        AppComponent,
        DeploymentsTableComponent,
        BannerComponent,
        ProductInformationComponent,
        LoginComponent,
        LogoutComponent,
        LoadingIndicatorComponent,
        AccountSelectedComponent,
        AccountSelectionComponent,
        SidebarComponent,
        DeploymentDetailsComponent,
        CsvDisplayPipe,
        UrlDisplayPipe,
        DeploymentTypePipe,
        PascalToHumanPipe,
        SKUDisplayPipe,
        ErrorDisplayTextPipe,
        DiskSizePipe,
        UpgradeDatePipe,
        OrgIdPipe,
        ScheduledUpgradeComponent,
        VerticalBarWidgetComponent
    ],
    imports: [
        RouterModule.forRoot(routes),
        BrowserModule,
        FormsModule,
        NgxChartsModule,
        HttpClientModule,
        CookieModule.forRoot(),
        ZFModalModule,
        ZFDropdownModule,
        AuthModule.forRoot({
            config: {
                authority: `https://cognito-idp.us-east-1.amazonaws.com/${environment.cognitoPool}`,
                postLoginRoute: 'login',
                redirectUrl: `${window.location.origin}/login`,
                postLogoutRedirectUri: `${window.location.origin}/logout`,
                clientId: environment.clientId,
                scope: 'aws.cognito.signin.user.admin openid',
                responseType: 'code',
                silentRenew: true,
                disablePkce: false,
                autoUserInfo: false,
                useRefreshToken: true,
                secureRoutes: [environment.provisioningApi],
                renewTimeBeforeTokenExpiresInSeconds: 10,
                logLevel: environment.production ? LogLevel.None : LogLevel.Debug
            },
        }),
    ],
    providers: [
        { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true },
        { provide: HTTP_INTERCEPTORS, useClass: InternalAuthInterceptor, multi: true },
        { provide: WINDOW_TOKEN, useFactory: windowProvider }
    ],
    bootstrap: [AppComponent]
})
export class AppModule { }

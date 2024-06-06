//  Angular imports
import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
//  Application imports
import { ApplicationRoute } from 'app/models/application-route';
import { DeploymentService } from 'app/services/deployment.service';
import { environment } from 'environments/environment';
import { RAccount } from 'app/records/account.record';
import { RAccountDetails } from 'app/records/account-details.record';
import { RActivatedStackInformation } from 'app/records/activated-stack-information.record';
import { RDeployment } from 'app/records/deployment.record';
import { RRegion } from 'app/records/region.record';
import { Selectable } from 'app/dropdown-module/models/selectable';
import { Status } from 'app/records/status.record';
import { UserService } from 'app/services/user.service';
import { ZFModalComponent } from 'app/modal-module';
//  Third party imports
import { finalize, tap, takeUntil, switchMap, retry, share } from 'rxjs/operators';
import { Subject, forkJoin, Observable, Subscription, timer } from 'rxjs';
import { RDeploymentType } from 'app/records/deployment-type.record';
import { ProvisionState } from 'app/models/provision-state';

@Component({
    selector: 'zf-deployments-table',
    templateUrl: './deployments-table.component.html',
    styleUrls: ['./deployments-table.component.scss']
})
export class DeploymentsTableComponent implements OnInit, OnDestroy {
    public get isProduction(): boolean {
        return environment.production;
    }

    public readonly productName: string = environment.productName;
    public readonly Status: any = Status;
    public readonly ProvisionState: any = ProvisionState;
    public readonly regions: Array<Selectable> =
        Object.keys(RRegion)
            .filter(
                (key: string): boolean => typeof RRegion[key] === 'string'
            )
            .map(
                (key: string): Selectable => new Selectable(RRegion.toDisplay.get(RRegion[key]), RRegion[key])
            )
            .sort(
                (a: Selectable, b: Selectable) => (a.display < b.display) ? -1 : (a.display > b.display) ? 1 : 0
            );

    public readonly deploymentTypes: Array<Selectable> =
        Object.keys(RDeploymentType)
            .filter(
                (key: string): boolean => typeof RDeploymentType[key] === 'string'
            )
            .map(
                (key: string): Selectable => new Selectable(RDeploymentType.toDisplay.get(RDeploymentType[key]), RDeploymentType[key])
            );

    public deployments: Array<RDeployment> = [];
    public activatedStackInformation: RActivatedStackInformation = new RActivatedStackInformation();
    public actionInProgress: boolean = false;
    public targetDeployment: RDeployment;
    public statusDeployment: RDeployment;
    public currentState: ProvisionState = ProvisionState.PROVISION;
    public refreshing: boolean = false;
    public ipV4: string = '';
    public ipV6: string = '';

    private readonly refreshTimeout: number = 5000;
    private account: RAccountDetails;
    private stopStatus$: Subject<void> = new Subject();
    private statusPoll$: Observable<RDeployment>;

    @ViewChild('activationModal')
    private activationModal: ZFModalComponent;

    @ViewChild('deleteConfirmationModal')
    private deleteConfirmationModal: ZFModalComponent;

    @ViewChild('updateConfirmationModal')
    private updateConfirmationModal: ZFModalComponent;

    @ViewChild('statusModal')
    private statusModal: ZFModalComponent;

    // container to hold existing subscriptions
    private subscriptions: Array<Subscription> = [];

    constructor(
        private router: Router,
        private userService: UserService,
        private deploymentsService: DeploymentService
    ) { }

    public ngOnInit(): void {
        this.activatedStackInformation.ipv4CIDRList = '0.0.0.0/0';
        this.activatedStackInformation.ipv6CIDRList = '::/0';
        this.ipV4 = '0.0.0.0/0';
        this.ipV6 = '::/0';
        this.subscriptions.push(
            this.userService.accountSelected$.subscribe(
                (account: RAccount): void => {
                    if (!!account) {
                        this.account = account.details;
                        this.getDeployments();
                    }
                }
            )
        );
    }

    public ngOnDestroy(): void {
        this.stopStatus();

        if (!!this.subscriptions) {
            this.subscriptions.forEach(
                (subscription: Subscription): void => subscription.unsubscribe()
            );
        }
    }

    public selectTargetDeployment(event: MouseEvent, deployment: RDeployment) {
        if (this.targetDeployment &&
            this.targetDeployment.serialNumber === deployment.serialNumber) {
            // we already have a value
            // so we clear it
            this.targetDeployment = null;
            return;
        }

        this.targetDeployment = deployment;
    }

    public prepareActivation(event: MouseEvent): void {
        event.stopPropagation();

        if (!this.targetDeployment || !this.targetDeployment.isValid) {
            this.currentState = ProvisionState.PRE_REQUISITE_FAILURE;
        } else {
            this.activatedStackInformation = new RActivatedStackInformation();
            this.currentState = ProvisionState.PROVISION;
        }

        setTimeout((): void => {
            this.activationModal.toggle();
        });
    }

    public prepareDelete(event: MouseEvent): void {
        event.stopPropagation();
        setTimeout((): void => this.deleteConfirmationModal.toggle());
    }

    public prepareUpdate(event: MouseEvent, deployment: RDeployment): void {
        event.stopPropagation();
        this.targetDeployment = deployment;
        setTimeout((): void => this.updateConfirmationModal.toggle());
    }

    public prepareStatus(event: MouseEvent, deployment: RDeployment): void {
        event.stopPropagation();
        this.statusDeployment = deployment;
        setTimeout((): void => this.statusModal.toggle());
        this.stopStatus();
        this.statusPoll$ = timer(1, 10000)
            .pipe(
                switchMap(() => this.getDeployment(this.statusDeployment.serialNumber)),
                retry(),
                share(),
                takeUntil(this.stopStatus$)

            );
        this.statusPoll$.subscribe((dep: RDeployment) => {
            if (dep) {
                this.statusDeployment = dep;
                if (this.statusDeployment.information.status === Status.COMPLETE) {
                    // we are complete
                    this.stopStatus$.next();
                }
            } else {
                // we've an error
                // we stop now
                this.stopStatus$.next();
            }
        });
    }

    public prepareProvision(event: MouseEvent): void {
        event.stopPropagation();

        // apply filter after split to remove empty entries
        // non-empty string is truthy
        // trim the start and end of the string
        this.ipV4 = this.ipV4.trim();
        this.ipV6 = this.ipV6.trim();
        this.activatedStackInformation.ipv4CIDRList = this.ipV4.split('\n').filter(i => i).join(',');
        this.activatedStackInformation.ipv6CIDRList = this.ipV6.split('\n').filter(i => i).join(',');

        // validate we have correct info
        if (!this.activatedStackInformation.validate()) { return; }

        this.currentState = ProvisionState.CONFIRMATION;
    }

    public stopStatus(): void {
        // cancel any running polls
        if (this.statusPoll$) {
            this.stopStatus$.next();
        }
    }

    public provisionRegion(): string {
        return RRegion.toDisplay.get(this.activatedStackInformation.region as RRegion);
    }

    public provisionDeploymentType(): string {
        return RDeploymentType.toDisplay.get(this.activatedStackInformation.deploymentType);
    }

    public editProvision(event: MouseEvent): void {
        event.stopPropagation();
        this.currentState = ProvisionState.PROVISION;
    }

    public closeProvision(event: MouseEvent): void {
        event.stopPropagation();
        this.activationModal.toggle();
    }

    public confirmDeployment(event: MouseEvent): void {
        event.stopPropagation();

        this.actionInProgress = true;

        // add new entries
        this.deploymentsService.activate(this.account.accountId, this.targetDeployment.serialNumber, this.activatedStackInformation)
            .pipe(
                finalize(
                    (): void => {
                        this.actionInProgress = false;
                        if (this.currentState === ProvisionState.NOT_APPROVED ||
                            this.currentState === ProvisionState.PRE_REQUISITE_FAILURE) {
                            // we need to show the NOT APPROVED content
                            // so don't close anything
                        } else {
                            this.activationModal.toggle();
                            this.targetDeployment = null;
                        }
                    }
                )
            )
            .subscribe({
                next: (): Subscription => this.getDeployment(this.targetDeployment.serialNumber).subscribe(),
                error: (error: HttpErrorResponse): void => {
                    if (error.status === 422) {
                        // we have a bad entitlement
                        this.currentState = ProvisionState.PRE_REQUISITE_FAILURE;
                    }
                    if (error.status === 403) {
                        // we have a forbidden activate
                        // this is a poc
                        this.currentState = ProvisionState.NOT_APPROVED;

                    }
                    // eslint-disable-next-line no-console
                    console.error(error.status, error.message);
                }
            });
    }

    public manage(): void {
        if (!this.targetDeployment) { return; }
        this.router.navigateByUrl(`${ApplicationRoute.ENTITLEMENTS}/${this.targetDeployment.serialNumber}`);
    }

    public getDeployments(): void {
        this.refreshing = true;
        forkJoin([
            timer(this.refreshTimeout),
            this.deploymentsService.getDeployments(this.account.accountId)
        ])
            .pipe(
                finalize(
                    (): boolean => this.refreshing = false
                )
            )
            .subscribe(
                ([_, deployments]: [number, Array<RDeployment>]): void => {
                    if (!deployments || !deployments.length) {
                        this.router.navigateByUrl(ApplicationRoute.PRODUCT_INFORMATION);
                    } else {
                        this.deployments = deployments;
                    }
                }
            );
    }

    public deleteDeployment(): void {
        if (!this.targetDeployment) { return; }
        this.actionInProgress = true;

        this.deploymentsService.deleteDeployment(this.account.accountId, this.targetDeployment.serialNumber)
            .pipe(
                finalize(
                    (): void => {
                        this.deleteConfirmationModal.toggle();
                        this.targetDeployment = null;
                        this.actionInProgress = false;
                    }
                )
            )
            .subscribe({
                next: (): Subscription => this.getDeployment(this.targetDeployment.serialNumber).subscribe(),
                error: (error: HttpErrorResponse): void => {
                    // eslint-disable-next-line no-console
                    console.error(error.message);
                }
            });
    }

    public updateDeployment(): void {
        if (!this.targetDeployment) { return; }
        this.actionInProgress = true;

        // force update on SKU
        // all the other elements will stay the same
        const activateInfo = new RActivatedStackInformation();
        activateInfo.shouldUpdateSKU = true;

        this.deploymentsService.update(this.account.accountId, this.targetDeployment.serialNumber,
            activateInfo)
            .pipe(
                finalize(
                    (): void => {
                        this.updateConfirmationModal.toggle();
                        this.targetDeployment = null;
                        this.actionInProgress = false;
                    }
                )
            )
            .subscribe({
                next: (): Subscription => this.getDeployment(this.targetDeployment.serialNumber).subscribe(),
                error: (error: HttpErrorResponse): void => {
                    // eslint-disable-next-line no-console
                    console.error(error.message);
                }
            });
    }

    public titleMessage(deployment: RDeployment): string {
        if (this.isDeploymentInWarningState(deployment)) {
            return 'Your instance will expire in less than 90 days';
        } else if (this.isDeploymentInExpiringState(deployment)) {
            return 'Your instance will expire in less than 30 days';
        }

        return '';
    }

    public isDeploymentInWarningState(deployment: RDeployment) {
        if (deployment?.entitlement?.compute?.expiryDays > 30 && deployment?.entitlement?.compute?.expiryDays <= 90) {
            return true;
        }

        return false;
    }

    public isDeploymentInExpiringState(deployment: RDeployment) {
        if (deployment?.entitlement?.compute?.expiryDays > 0 && deployment?.entitlement?.compute?.expiryDays <= 30) {
            return true;
        }

        return false;
    }

    private getDeployment(serialNumber: string, delay: number = 0): Observable<RDeployment> {
        return this.deploymentsService.getDeployment(this.account.accountId, serialNumber)
            .pipe(
                tap(
                    (deployment: RDeployment): void => {
                        setTimeout((): void => {
                            const index: number = this.deployments.findIndex(
                                (_deployment: RDeployment): boolean => _deployment.serialNumber.toLowerCase() === serialNumber.toLowerCase()
                            );
                            this.deployments[index] = deployment;
                        }, delay);
                    }
                )
            );
    }
}

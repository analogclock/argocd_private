//  Angular imports
import { ActivatedRoute, Params } from '@angular/router';
import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
//  Application imports
import { ApplicationRoute } from 'app/models/application-route';
import { DeploymentService } from 'app/services/deployment.service';
import { RAccount } from 'app/records/account.record';
import { RAccountDetails } from 'app/records/account-details.record';
import { RDeployment } from 'app/records/deployment.record';
import { RActivatedStackInformation } from 'app/records/activated-stack-information.record';
import { UserService } from 'app/services/user.service';
//  Third party imports
import { finalize } from 'rxjs/operators';
import { Subscription } from 'rxjs';
import { Status } from 'app/records/status.record';
import { ZFModalComponent } from 'app/modal-module/zf-modal.component';
import { RAlternateCertificate } from 'app/records/alternate-certificate.record';
import { LegendPosition } from '@swimlane/ngx-charts';
import { LineChartSeries, LineChartSlice, PieChartSlice, ReferenceLine } from 'app/models/pie-chart-slice';
import { DiskCalculator } from 'app/pipes/disk-calculator';
import { MetricsService } from 'app/services/metrics.service';
import { RMetricData } from 'app/records/metric-data.record';

import * as forge from 'node-forge';
import { VersionService } from 'app/services/version.service';
import { RVersion } from 'app/records/version.record';
import { environment } from 'environments/environment';
import { UpgradeService } from 'app/services/upgrade.service';
import { RUpgradeModel } from 'app/models/upgrade-model';
import { RActivation } from 'app/records/activation.record';
import { ExternalStorageService } from 'app/services/external.storage.service';
import { RExternalStorageDetailModel } from 'app/models/external-storage-detail-model';
import { RStorageData, RStorageDataRow } from 'app/records/storage-data.record';
import { formatDate } from '@angular/common';

@Component({
    selector: 'zf-deployment-details',
    templateUrl: './deployment-details.component.html',
    styleUrls: ['./deployment-details.component.scss']
})
export class DeploymentDetailsComponent implements OnInit, OnDestroy {
    public get isProduction(): boolean {
        return environment.production;
    }
    public readonly ApplicationRoute: typeof ApplicationRoute = ApplicationRoute;
    public readonly LegendPosition: typeof LegendPosition = LegendPosition;
    public serialNumber: string;
    public deployment: RDeployment;

    public refLines: Array<ReferenceLine> = [];
    public hasUpdate: boolean = false;
    public hasScheduledUpdate: boolean = false;
    public versionUpdate: RVersion = null;

    // the following are all editable fields which the user can change after
    // deployments
    public editing: boolean = false;
    public activatedStackInfo: RActivatedStackInformation = new RActivatedStackInformation();
    public ipV4: string = '';
    public ipV6: string = '';
    public deploymentEmail: string = '';
    public additionalContacts: string = '';
    public certificateBody: string = '';
    public certificatePrivate: string = '';
    public certificateChain: string = '';
    public alternateDomain: string = '';
    public certificatePassword: string = '';
    public certificate: forge.pki.Certificate = null;
    public tmpCertificate: File = null;
    public certificateFilePath: string = '';
    public certificateManual: boolean = false;
    public extractionError: string = '';
    public externalStorageOrganization: string = '';
    public externalStorageDest: string = '';
    public externalStorageBucket: string = '';
    public externalStorageDirectory: string = '';
    public externalStoragePolicy: object = undefined;
    public externalStorageLoading: boolean = true;

    // Used to immediately disable Update button once clicked
    public updating: boolean = false;
    public displayRegion: string;
    public eventsTime: string = 'day';
    public storageInfoView: boolean = false;
    public onlineStorageView: string = 'chart';
    public archiveStorageView: string = 'chart';
    public onlineStorageInfo: Array<PieChartSlice> = [];
    public archiveStorageInfo: Array<PieChartSlice> = [];
    public eventsPerSecInfo: Array<LineChartSeries> = [];

    public onlineStorageMetrics: Array<LineChartSeries>;
    public archiveStorageMetrics: Array<LineChartSeries>;

    public extStorages: Array<RExternalStorageDetailModel> = [];
    public selectedSto: RExternalStorageDetailModel;

    public editState: string = 'network';
    public certificateState: string = 'file';

    public scheduling: boolean = false;
    public minUpdateDate: Date = new Date();
    public maxUpdateDate: Date = new Date();
    public scheduledDate: string;
    public upgrade: RUpgradeModel = new RUpgradeModel();
    public newStorage: boolean = true;
    public storageDetail: RExternalStorageDetailModel = new RExternalStorageDetailModel();
    public deletingStorage: boolean = false;

    public changingStorages: boolean = false;

    @ViewChild('editModal')
    private editModal: ZFModalComponent;

    @ViewChild('scheduleModal')
    private scheduleModal: ZFModalComponent;

    @ViewChild('storageModal')
    private storageModal: ZFModalComponent;

    private account: RAccountDetails;
    private subscriptions: Array<Subscription> = [];

    constructor(
        private route: ActivatedRoute,
        private userService: UserService,
        private deploymentService: DeploymentService,
        private metricsService: MetricsService,
        private versionService: VersionService,
        private upgradeService: UpgradeService,
        private externalStorageService: ExternalStorageService
    ) { }

    public ngOnInit(): void {
        this.subscriptions.push(
            this.route.params.subscribe(
                (params: Params): void => {
                    this.serialNumber = params.serial;
                    this.getAccount();
                }
            )
        );

        // minimum date is today + 1 day (tomorrow)
        this.minUpdateDate.setDate(this.minUpdateDate.getDate() + 1);
        // max 2 months from today
        this.maxUpdateDate.setDate(this.minUpdateDate.getDate() + 60);
    }

    public ngOnDestroy(): void {
        if (!!this.subscriptions) {
            this.subscriptions.forEach(
                (subscription: Subscription): void => subscription.unsubscribe()
            );
        }
    }

    public isUpdatePossible(deployment: RDeployment): boolean {
        return deployment.information.status === Status.LICENSE_IN_PROGRESS ||
            deployment.information.status === Status.CREATE_FAILED ||
            deployment.information.status === Status.UPDATE_COMPLETED ||
            deployment.information.status === Status.UPDATE_FAILED ||
            deployment.information.status === Status.COMPLETE;
    }

    public edit(): void {
        this.editing = true;
        // clear any residual values if we ran edit previously
        this.ipV4 = this.deployment.information.ipV4Cidr.fromCsv() ?? '';
        this.ipV6 = this.deployment.information.ipV6Cidr.fromCsv() ?? '';
        this.additionalContacts = this.deployment?.information?.additionalContacts?.fromCsv() ?? '';
        this.externalStorageDest = this.deployment?.information?.externalStorageDest;
        const [bucket, ...rest] = this.externalStorageDest.split('/');
        this.externalStorageBucket = bucket;
        this.externalStorageDirectory = rest.length > 0 ? rest.join('/') : '';

        this.generatePolicy();

        this.certificateBody = '';
        this.certificatePrivate = '';
        this.certificateChain = '';
        this.extractionError = '';
        this.certificatePassword = '';
        this.certificate = null;
        this.certificateFilePath = '';
        this.activatedStackInfo = new RActivatedStackInformation();

        setTimeout(() => {
            this.editModal.toggle();
        });
    }

    public schedule(): void {
        this.scheduling = true;
        setTimeout(() => {
            this.scheduleModal.toggle();
        });
    }

    public storage(id?: string, isDelete: boolean = false): void {
        this.changingStorages = true;

        if (!id) {
            this.newStorage = true;
            this.storageDetail = new RExternalStorageDetailModel();
            this.storageDetail.serialNumber = this.serialNumber;
            // default to all
            this.storageDetail.organizationId = -1;
            this.externalStorageBucket = '';
            this.externalStorageDirectory = '';
            this.externalStoragePolicy = undefined;
        } else {
            this.newStorage = false;
            const fromArray = this.extStorages.find(x => x.id === id);
            Object.assign<RExternalStorageDetailModel, RExternalStorageDetailModel>(this.storageDetail, fromArray);
            const [bucket, ...rest] = this.storageDetail.externalStorageDest.split('/');
            this.externalStorageBucket = bucket;
            this.externalStorageDirectory = rest.length > 0 ? rest.join('/') : '';
            this.generatePolicy();
        }

        this.deletingStorage = isDelete;

        setTimeout(() => {
            this.storageModal.toggle();
        });
    }

    public addToStorage(event: MouseEvent) {
        event.stopPropagation();

        if (!this.storageDetail.validate()) {
            // stop do not proceed
            return;
        }

        this.externalStorageService.addStorage(this.account.accountId, this.storageDetail).subscribe((act: RActivation) => {
            if (act) {
                this.changingStorages = false;
                this.storageModal.toggle();
                this.getExternalStorage(this.account.accountId, this.serialNumber);
            }
            this.storageDetail = new RExternalStorageDetailModel();

        });

    }

    public deleteFromStorage(event: MouseEvent) {
        event.stopPropagation();

        this.externalStorageService.deleteStorage(this.account.accountId, this.storageDetail).subscribe((act: RActivation) => {
            if (act) {
                this.changingStorages = false;
                this.storageModal.toggle();
                this.getExternalStorage(this.account.accountId, this.serialNumber);
            }
            this.storageDetail = new RExternalStorageDetailModel();
            this.selectedSto = null;
        });
    }

    public updateScheduledDate(event: string) {
        if (event) {
            this.scheduledDate = event;
        }
    }

    public scheduleUpdate(event: MouseEvent): void {
        event.stopPropagation();

        const upgrade = new RUpgradeModel();
        upgrade.serialNumber = this.deployment.serialNumber;
        upgrade.scheduledLocal = this.scheduledDate;
        upgrade.upgradePath = this.versionUpdate.upgradePath;
        this.upgradeService.addSchedule(this.account.accountId, this.deployment.serialNumber, upgrade).subscribe((act: RActivation) => {
            if (act) {
                this.scheduleModal.toggle();
                this.checkForUpdate(this.account.accountId, this.serialNumber);
            }
        });
    }

    public refresh(): void {
        this.deployment = null;
        this.hasUpdate = false;
        this.eventsPerSecInfo = [];
        this.onlineStorageMetrics = null;
        this.archiveStorageMetrics = null;
        this.getDeployment(this.account.accountId);
    }

    public editValidate(event: MouseEvent): void {
        event.stopPropagation();

        // re-parse CIDRs into comma-separated items
        // trim the strings
        this.ipV4 = this.ipV4 ? this.ipV4.trim() : '';
        this.ipV6 = this.ipV6 ? this.ipV6.trim() : '';
        this.additionalContacts = this.additionalContacts ? this.additionalContacts.trim() : '';
        this.alternateDomain = this.alternateDomain ? this.alternateDomain.trim() : '';

        this.activatedStackInfo.ipv4CIDRList = this.ipV4.toCsv();
        this.activatedStackInfo.ipv6CIDRList = this.ipV6.toCsv();
        this.activatedStackInfo.additionalContacts = this.additionalContacts.toCsv();
        this.activatedStackInfo.alternateDomain = this.alternateDomain.trim();
        let checkDomain: boolean = false;

        if (this.activatedStackInfo.alternateDomain !== this.deployment.information.alternateDomain) {
            // we have a difference
            if (this.activatedStackInfo.alternateDomain && !this.deployment.information.alternateDomain) {
                // if we have a value in the settings
                // where previously we didn't
                // then we are adding
                checkDomain = true;
            }

            // we must be removing
            // don't recheck
        }

        if (this.certificateBody) {
            this.activatedStackInfo.certificate = new RAlternateCertificate();
            this.activatedStackInfo.certificate.body = this.certificateBody;
            this.activatedStackInfo.certificate.private = this.certificatePrivate;
            this.activatedStackInfo.certificate.chain = this.certificateChain;
            checkDomain = true;
        }


        // validating update info looks good
        if (!this.activatedStackInfo.validate(true, checkDomain)) {
            if (this.activatedStackInfo.error['ipv4'] || this.activatedStackInfo.error['ipv6']) {
                this.editState = 'network';
            }

            if (this.activatedStackInfo.error['additionalContacts']) {
                this.editState = 'notifications';
            }

            if (this.activatedStackInfo.error['alternateDomain'] ||
                this.activatedStackInfo.error['alternatePublicCertificate'] ||
                this.activatedStackInfo.error['alternatePrivateCertificate'] ||
                this.activatedStackInfo.error['alternateChainCertificate']) {
                this.editState = 'domain';
            }

            return;
        }

        this.editState = 'confirmation';
    }

    public updateFullBucket(): void {
        let tmpDest = this.externalStorageBucket;
        if (this.externalStorageDirectory.length > 0) {
            const tmpDir = this.externalStorageDirectory.replaceMultipleSlashes();
            tmpDest = `${tmpDest}/${tmpDir}${tmpDir.endsWith('/') ? '' : '/'}`;
        }
        this.storageDetail.externalStorageDest = tmpDest;
        this.generatePolicy();
    }

    public update(deployment: RDeployment, event: MouseEvent): void {
        event.stopPropagation();

        // re-parse CIDRs into comma-separated items
        // trim the strings
        this.ipV4 = this.ipV4 ? this.ipV4.trim() : '';
        this.ipV6 = this.ipV6 ? this.ipV6.trim() : '';
        this.additionalContacts = this.additionalContacts ? this.additionalContacts.trim() : '';
        this.alternateDomain = this.alternateDomain ? this.alternateDomain.trim() : '';

        this.activatedStackInfo.ipv4CIDRList = this.ipV4.toCsv();
        this.activatedStackInfo.ipv6CIDRList = this.ipV6.toCsv();
        this.activatedStackInfo.additionalContacts = this.additionalContacts.toCsv();
        this.activatedStackInfo.externalStorageDest = this.externalStorageDest;

        let checkDomain: boolean = false;
        this.activatedStackInfo.alternateDomain = this.alternateDomain;

        // do we have a value for the alternate
        if (this.alternateDomain && this.alternateDomain !== this.deployment.information.alternateDomain) {
            checkDomain = true;
        }

        // validating update info looks good
        if (!this.activatedStackInfo.validate(true, checkDomain)) { return; }

        this.updating = true;

        this.deploymentService.update(this.account.accountId, deployment.serialNumber, this.activatedStackInfo)
            .pipe(
                finalize(
                    (): void => {
                        this.updating = deployment.information.status === Status.UPDATE_IN_PROGRESS;
                        this.editing = false;
                        this.editModal.toggle();
                    }
                )
            )
            .subscribe({
                next: (): void => this.getDeployment(this.account.accountId),
                error: (error: HttpErrorResponse): void => {
                    // eslint-disable-next-line no-console
                    console.error(error.message);
                }
            });
    }

    public toGBytes(bytes: number): number {
        const value = bytes ?? 0;
        const toSize = value;
        const num = Math.round((toSize + Number.EPSILON) * 100) / 100;

        // take the value divide until we get to GB
        // and then return a fixed to 2 decimal number back
        return num / (1024 * 1024 * 1024);
    }

    public copyToClipboard(event: MouseEvent, input: string) {
        event.preventDefault();
        if (!input) {
            return;
        }
        input = input.endsWith('.') ? input.stripLast().stripProtocol() : input.stripProtocol();
        navigator.clipboard.writeText(input);
        alert(`Copied ${input} to clipboard`);
    }

    public copyToClipboardObject(event: MouseEvent, input: object) {
        event.preventDefault();
        if (!input) {
            return;
        }
        const jsonStr: string = JSON.stringify(input, null, 4);
        navigator.clipboard.writeText(jsonStr);
        alert('Copied AWS policy to clipboard');
    }

    public refreshMetrics(): void {
        this.getMetrics(this.account.accountId, this.serialNumber, this.deployment.allocatedEPS);
    }

    public setCertificate(event: Event): void {
        const eventTarget: HTMLInputElement = event.target as HTMLInputElement;
        const cert: File = eventTarget.files.item(0);

        if (this.extractionError) {
            this.extractionError = '';
        }

        if (cert.type !== 'application/x-pkcs12') {
            // the type is not of th expected format
            this.extractionError = 'File type is not PKCS#12 (.p12).';
            return;
        }

        // max file size for pkcs#12 is 40KB
        if (cert.size >= (40 * 1024 * 1024)) {
            this.extractionError = 'PKCS#12 file exceeds maximum allowed.';
            return;
        }

        this.tmpCertificate = cert;
        this.certificateFilePath = cert.name;
    }

    public handleCertificate(event: Event): void {

        event.stopPropagation();
        if (this.extractionError) {
            this.extractionError = '';
        }

        const cert = this.tmpCertificate;
        const reader: FileReader = new FileReader();
        reader.onload = (ev: ProgressEvent<FileReader>) => {
            try {
                // read data from file reader into DER format (pkcs12 is der format)
                const p12Asn1 = forge.asn1.fromDer(reader.result as any);

                // create our p12 object, using the provided password
                const p12 = forge.pkcs12.pkcs12FromAsn1(p12Asn1, this.certificatePassword);

                // this is the main certificate bag (will contain 2 (public cert, ca certs))
                const certBags = p12.getBags({ bagType: forge.pki.oids.certBag });

                // get the private certificate
                const pkeyBags = p12.getBags({ bagType: forge.pki.oids.pkcs8ShroudedKeyBag });
                const allCerts = certBags[forge.pki.oids.certBag];

                // main certificate is here always
                const mainCertificate: forge.pki.Certificate = allCerts[0].cert;
                this.certificate = mainCertificate;
                // if we have more than 1 use the first one as the CA certificate
                const chainCertificate: forge.pki.Certificate = allCerts.length > 1 ? allCerts[1].cert : null;

                // fetching keyBag
                const keybag = pkeyBags[forge.pki.oids.pkcs8ShroudedKeyBag][0];
                // generate pem from private key
                const privateKeyPem = forge.pki.privateKeyToPem(keybag.key);
                // generate pem from cert
                const certificatePem: string = forge.pki.certificateToPem(mainCertificate);
                // generate pem from CA chain - it can be empty
                const chainCertPem: string = chainCertificate !== null ? forge.pki.certificateToPem(chainCertificate) : '';
                const certCN = mainCertificate.subject.getField('CN')?.value ?? 'unresolved';

                this.certificateBody = certificatePem;
                this.certificatePrivate = privateKeyPem;
                this.certificateChain = chainCertPem;
                this.alternateDomain = certCN;
            } catch (e: any) {
                // capture any extraction errors
                this.extractionError = e;
            }
        };

        // trigger the read
        reader.readAsBinaryString(cert);
    }

    public formatDiskSize(value: number): string {
        return DiskCalculator.toHuman(value, 2);
    }

    private generatePolicy(): void {
        if (this.externalStorageBucket.length === 0) {
            // settings this to undefined means it won't
            // show up as `{}` in the text area
            this.externalStoragePolicy = undefined;
            return;
        }

        /* eslint-disable @typescript-eslint/naming-convention */
        this.externalStoragePolicy = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Resource': `arn:aws:s3:::${this.externalStorageBucket}/*`,
                    'Effect': 'Allow',
                    'Principal': {
                        'AWS': `${this.deployment.information.externalStorage}`
                    },
                    'Action': 's3:PutObject'
                },
                {
                    'Resource': `arn:aws:s3:::${this.externalStorageBucket}`,
                    'Effect': 'Allow',
                    'Principal': {
                        'AWS': `${this.deployment.information.externalStorage}`
                    },
                    'Action': 's3:ListBucket'
                }
            ]
        };
        /* eslint-enable @typescript-eslint/naming-convention */
    }

    private getAccount(): void {
        this.subscriptions.push(
            this.userService.accountSelected$
                .subscribe(
                    (account: RAccount): void => {
                        if (!!account) {
                            this.account = account.details;
                            this.getDeployment(this.account.accountId);
                        }
                    }
                )
        );
    }

    private getDeployment(accountId: number): void {
        this.checkForUpdate(accountId, this.serialNumber);

        this.deploymentService.getDeployment(accountId, this.serialNumber).subscribe(
            (deployment: RDeployment): RDeployment => {
                this.deployment = deployment;
                this.ipV4 = this.deployment.information.ipV4Cidr.split(',').join('\n');
                this.ipV6 = this.deployment.information.ipV6Cidr.split(',').join('\n');
                this.alternateDomain = this.deployment.information.alternateDomain;
                this.additionalContacts = deployment?.information?.additionalContacts?.split(',').join('\n');
                this.displayRegion = deployment.information.displayRegion;
                this.getExternalStorage(accountId, this.deployment.serialNumber);
                this.getStorageMetrics(accountId, this.deployment.serialNumber);
                this.getStorageInfo();
                this.getMetrics(accountId, this.deployment.serialNumber, deployment.allocatedEPS);
                return this.deployment;
            }
        );
    }

    private checkForUpdate(accountId: number, serialNumber: string): void {
        this.versionService.checkForUpdate(accountId, serialNumber).subscribe(
            (versions: Array<RVersion>): void => {
                if (versions.length > 0) {
                    this.upgradeService.hasUpgradeScheduled(accountId, serialNumber)
                        .subscribe((upgrades: Array<RUpgradeModel>) => {
                            this.hasUpdate = true;
                            this.versionUpdate = versions.at(0);
                            this.hasScheduledUpdate = false;
                            if (upgrades.length > 0) {
                                const scheduled = upgrades.find((u) => u.upgradePath === versions.at(0).upgradePath);
                                if (scheduled && scheduled.status === 'Pending') {
                                    this.hasScheduledUpdate = true;
                                    this.upgrade = scheduled;
                                    this.scheduledDate = scheduled.scheduledLocal;
                                }
                            }
                        });
                }
            });
    }

    private getExternalStorage(accountId: number, serialNumber: string) {
        this.externalStorageLoading = true;
        this.extStorages = [];
        this.externalStorageService.getExternalStorages(accountId, serialNumber)
            .subscribe((d: Array<RExternalStorageDetailModel>) => {
                this.externalStorageLoading = false;
                this.extStorages = d;
            });
    }

    private getStorageMetrics(accountId: number, serialNumber: string) {
        this.metricsService.getStorageMetrics(accountId, serialNumber).subscribe((storageData: RStorageDataRow) => {
            this.onlineStorageMetrics = [];
            this.archiveStorageMetrics = [];

            if (!storageData) {
                return;
            }

            const onlineSeries = storageData.online
                ? this.getBarChartData('Online', storageData.online.unique('day'))
                : null;
            const archiveSeries = storageData.archive
                ? this.getBarChartData('Archive', storageData.archive.unique('day'))
                : null;

            if (onlineSeries && onlineSeries.length > 0) {
                this.onlineStorageMetrics = onlineSeries;
            }

            if (archiveSeries && archiveSeries.length > 0) {
                this.archiveStorageMetrics = archiveSeries;
            }
        });
    }
    private getBarChartData(seriesLabel: string, items: Array<RStorageData>): Array<LineChartSeries> {
        const data: Array<LineChartSeries> = [];
        for (const metric of items.sort((a, b) => new Date(a.day).valueOf() - new Date(b.day).valueOf())) {
            data.push(new LineChartSeries(metric.day, [
                new LineChartSlice(seriesLabel, metric.bytes)
            ]));
        }
        return data;
    }

    private getMetrics(accountId: number, serialNumber: string, maxAllowed: number): void {
        this.eventsPerSecInfo = [];
        this.refLines = [{
            name: 'Allocated compute',
            value: maxAllowed
        }];

        this.metricsService.getMetrics(accountId, serialNumber, 'Events', this.eventsTime).subscribe(
            (d: Array<RMetricData>) => {
                let dropFirst = true;
                const lineChartData: Array<LineChartSlice> = [];
                for (const metric of d) {
                    if (dropFirst) {
                        dropFirst = false;
                        continue;
                    }
                    const data = new LineChartSlice(new Date(metric.key), metric.value);
                    lineChartData.push(data);
                }
                const series = new LineChartSeries('Events per second', lineChartData);
                this.eventsPerSecInfo.push(series);
            }
        );
    }

    private getStorageInfo(): void {
        if (!this.deployment) {
            return;
        }

        const onlineStorageCap = this.fromQuantityToBytes(this.deployment.entitlement.onlineStorage?.quantity ?? 0);
        const archiveStorageCap = this.fromQuantityToBytes(this.deployment.entitlement.archiveStorage?.quantity ?? 0);
        let online = this.deployment.information.onlineSizeUsage ?? 0;
        let archive = this.deployment.information.archiveSizeUsage ?? 0;

        if (online > onlineStorageCap) {
            online = onlineStorageCap - 0.1;
        }

        if (archive > archiveStorageCap) {
            archive = archiveStorageCap - 0.1;
        }

        const onlineUsed = online > 0 ? online : 0;
        const onlineFree = online > 0 ? onlineStorageCap - online : onlineStorageCap;
        const archiveUsed = archive > 0 ? archive : 0;
        const archiveFree = archive > 0 ? archiveStorageCap - archive : archiveStorageCap;
        this.onlineStorageInfo = [
            {
                name: `used (${DiskCalculator.toHuman(onlineUsed, 2)})`, value: onlineUsed
            },
            {
                name: `free (${DiskCalculator.toHuman(onlineFree, 2)})`, value: onlineFree
            },
        ];

        this.archiveStorageInfo = [
            {
                name: `used (${DiskCalculator.toHuman(archiveUsed, 2)})`, value: archiveUsed
            },
            {
                name: `free (${DiskCalculator.toHuman(archiveFree, 2)})`, value: archiveFree
            },
        ];

    }

    private fromQuantityToBytes(quantity: number): number {
        const value = quantity ?? 0;
        const bytes = (value * (500 * 1000 * 1000 * 1000));
        return bytes;
    }
}

//  Angular imports
import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { FormsModule } from '@angular/forms';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { RouterTestingModule } from '@angular/router/testing';
//  Application imports
import { DeploymentService } from 'app/services/deployment.service';
import { DeploymentServiceMock } from 'app/services/deployment.service.mock';
import { DeploymentsTableComponent } from './deployments-table.component';
import { RAccountDetails } from 'app/records/account-details.record';
import { RActivation } from 'app/records/activation.record';
import { RDeployment } from 'app/records/deployment.record';
import { Status } from 'app/records/status.record';
import { UserService } from 'app/services/user.service';
import { UserServiceMock } from 'app/services/user.service.mock';
import { ZFModalComponent, ZFModalComponentMock, ZFModalModule } from 'app/modal-module';
//  Third party imports
import { of } from 'rxjs';

const deployments: Array<RDeployment> = [
    {
        serialNumber: '012',
        description: 'dummy-description-1',
        entitlement: {
            startDate: 'today',
            endDate: 'next Wednesday',
            devices: 100,
            advancedAgents: 225,
            totalStorage: 10,
            totalEPS: 10000,
            expiryDays: 3
        },
        information: {
            serialNumber: 'some-dummy-number',
            url: 'dummy-url',
            status: Status.CREATE_IN_PROGRESS,
            created: 'just now'
        }
    },
    {
        serialNumber: '015',
        description: 'dummy-description-2',
        entitlement: {
            startDate: 'last week',
            endDate: 'round Xmas',
            devices: 200,
            advancedAgents: 525,
            totalStorage: 12,
            totalEPS: 15000,
            expiryDays: 2
        },
        information: {
            serialNumber: 'some-dummy-number',
            url: 'dummy-url',
            status: Status.CREATE_IN_PROGRESS,
            created: 'just now'
        }
    }
];

describe('DeploymentsTableComponent', (): void => {
    let component: DeploymentsTableComponent;
    let fixture: ComponentFixture<DeploymentsTableComponent>;

    beforeEach(waitForAsync((): void => {
        TestBed.configureTestingModule({
            imports: [
                RouterTestingModule,
                FormsModule,
                ZFModalModule
            ],
            declarations: [ DeploymentsTableComponent ],
            schemas: [ NO_ERRORS_SCHEMA ],
            providers: [
                { provide: UserService, useClass: UserServiceMock },
                { provide: DeploymentService, useClass: DeploymentServiceMock }
            ]
        }).compileComponents();
    }));

    beforeEach((): void => {
        fixture = TestBed.createComponent(DeploymentsTableComponent);
        component = fixture.componentInstance;
        component['account'] = { accountId: 1 } as RAccountDetails;
    });

    it('should create', (): void => {
        expect(component).toBeTruthy();
    });

    it('should initialise component', (): void => {
        spyOn(component as any, 'getDeployments');
        component.ngOnInit();
        expect(component.getDeployments).toHaveBeenCalled();
    });

    it('should open activation modal with the right deployment', waitForAsync((): void => {
        component['activationModal'] = new ZFModalComponentMock() as any as ZFModalComponent;
        spyOn(component['activationModal'], 'toggle');
        const event: MouseEvent = { stopPropagation: (): void => {} } as MouseEvent;
        spyOn(event, 'stopPropagation');
        component.prepareActivation(event);
        expect(event.stopPropagation).toHaveBeenCalled();
        setTimeout( (): void => expect(component['activationModal'].toggle).toHaveBeenCalled() );
    }));

    it('should activate if user is valid', waitForAsync((): void => {
        component['activationModal'] = new ZFModalComponentMock() as any as ZFModalComponent;
        component.targetDeployment = deployments[2];
        spyOnProperty(component.activatedStackInformation, 'valid', 'get').and.returnValue(true);
        const activation: RActivation = new RActivation();
        activation.id = 'fakeStackId';
        spyOn(component['deploymentsService'], 'activate').and.returnValue(of(activation));
        spyOn(component['activationModal'], 'toggle');
        spyOn(component as any, 'getDeployment').and.returnValue(of());
        const event: MouseEvent = { stopPropagation: (): void => {} } as MouseEvent;
        spyOn(event, 'stopPropagation');
        component.activate(deployments[0], event);
        expect(event.stopPropagation).toHaveBeenCalled();
        setTimeout( (): void => {
            expect(component['getDeployment']).toHaveBeenCalledWith(deployments[0].serialNumber);
            expect(component['activationModal'].toggle).toHaveBeenCalled();
            expect(component.targetDeployment).toBeNull();
        } );
    }));

    it('should not activate if user is invalid', (): void => {
        component['activationModal'] = new ZFModalComponentMock() as any as ZFModalComponent;
        component.targetDeployment = deployments[0];
        spyOnProperty(component.activatedStackInformation, 'valid', 'get').and.returnValue(false);
        const activation: RActivation = new RActivation();
        activation.id = 'fakeStackId';
        spyOn(component['deploymentsService'], 'activate').and.returnValue(of(activation));
        spyOn(component['activationModal'], 'toggle');
        spyOn(component as any, 'getDeployment').and.returnValue(of());
        const event: MouseEvent = { stopPropagation: (): void => {} } as MouseEvent;
        spyOn(event, 'stopPropagation');
        component.activate(deployments[0], event);
        expect(event.stopPropagation).toHaveBeenCalled();
        expect(component['getDeployment']).not.toHaveBeenCalled();
        expect(component['activationModal'].toggle).not.toHaveBeenCalled();
        expect(component.targetDeployment).toBe(deployments[0]);
    });

    it('should get deployments', waitForAsync((): void => {
        (component as any)['refreshTimeout'] = 10;
        spyOn(component['deploymentsService'] as any, 'getDeployments').and.returnValue(of(deployments));
        component.getDeployments();
        setTimeout( (): void => expect(component.deployments).toEqual([deployments[0], deployments[1]]), 10 );
    }));

    it('should not delete deployment if deployment is not selected', (): void => {
        spyOn(component['deploymentsService'] as any, 'deleteDeployment').and.returnValue(of(true));
        spyOn(component, 'getDeployments');
        component.deleteDeployment();
        expect(component.getDeployments).not.toHaveBeenCalled();
    });

    it('should delete deployment if deployment is selected', (): void => {
        component.targetDeployment = new RDeployment();
        component.targetDeployment.serialNumber = 'dummy-serial';
        spyOn(component['deploymentsService'] as any, 'deleteDeployment').and.returnValue(of(true));
        spyOn(component, 'getDeployments');
        component.deleteDeployment();
        expect(component['deploymentsService'].deleteDeployment).toHaveBeenCalledOnceWith(1, 'dummy-serial');
        expect(component.getDeployments).toHaveBeenCalled();
    });

    it('should get deployment', (): void => {
        spyOn(component['deploymentsService'], 'getDeployment').and.returnValue(of());
        component['getDeployment'](deployments[1].serialNumber);
        expect(component['deploymentsService'].getDeployment).toHaveBeenCalledWith(1, deployments[1].serialNumber);
    });
});

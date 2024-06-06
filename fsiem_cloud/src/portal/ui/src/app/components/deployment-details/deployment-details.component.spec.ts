//  Angular imports
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
//  Application imports
import { DeploymentDetailsComponent } from './deployment-details.component';
import { DeploymentService } from 'app/services/deployment.service';
import { DeploymentServiceMock } from 'app/services/deployment.service.mock';
import { UserService } from 'app/services/user.service';
import { UserServiceMock } from 'app/services/user.service.mock';

describe('DeploymentDetailsComponent', (): void => {
    let component: DeploymentDetailsComponent;
    let fixture: ComponentFixture<DeploymentDetailsComponent>;

    beforeEach((): void => {
        TestBed.configureTestingModule({
            imports: [ RouterTestingModule ],
            declarations: [ DeploymentDetailsComponent ],
            providers: [
                { provide: UserService, useClass: UserServiceMock },
                { provide: DeploymentService, useClass: DeploymentServiceMock }
            ]
        }).compileComponents();
    });

    beforeEach((): void => {
        fixture = TestBed.createComponent(DeploymentDetailsComponent);
        component = fixture.componentInstance;
    });

    it('should create', (): void => {
        expect(component).toBeTruthy();
    });
});

//  Angular imports
import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';
//  Application imports
import { AppComponent } from './app.component';
import { UserService } from 'app/services/user.service';
import { UserServiceMock } from 'app/services/user.service.mock';

describe('AppComponent', (): void => {
    let fixture: ComponentFixture<AppComponent>;
    let app: AppComponent;

    beforeEach(waitForAsync((): void => {
        TestBed.configureTestingModule({
            declarations: [
                AppComponent
            ],
            schemas: [ NO_ERRORS_SCHEMA ],
            providers: [
                { provide: UserService, useClass: UserServiceMock }
            ]
        }).compileComponents();
    }));

    beforeEach((): void => {
        fixture = TestBed.createComponent(AppComponent);
        app = fixture.debugElement.componentInstance;
    });

    it('should create the app', (): void => {
        expect(app).toBeTruthy();
    });
});

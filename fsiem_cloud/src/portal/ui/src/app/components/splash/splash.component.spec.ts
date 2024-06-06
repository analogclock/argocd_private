//  Angular imports
import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
//  Application imports
import { SplashComponent } from './splash.component';

describe('SplashComponent', (): void => {
    let component: SplashComponent;
    let fixture: ComponentFixture<SplashComponent>;

    beforeEach(waitForAsync((): void => {
        TestBed.configureTestingModule({
            declarations: [ SplashComponent ]
        }).compileComponents();
    }));

    beforeEach((): void => {
        fixture = TestBed.createComponent(SplashComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', (): void => {
        expect(component).toBeTruthy();
    });
});

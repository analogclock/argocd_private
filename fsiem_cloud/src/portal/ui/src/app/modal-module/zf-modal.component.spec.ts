//  Angular imports
import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
//  Application imports
import { ZFModalComponent } from './zf-modal.component';

describe('ZFModalComponent', (): void => {
    let component: ZFModalComponent;
    let fixture: ComponentFixture<ZFModalComponent>;

    beforeEach(waitForAsync((): void => {
        TestBed.configureTestingModule({
            declarations: [ ZFModalComponent ]
        }).compileComponents();
    }));

    beforeEach((): void => {
        fixture = TestBed.createComponent(ZFModalComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', (): void => {
        expect(component).toBeTruthy();
    });
});

//  Angular imports
import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
//  Application imports
import { ProductInformationComponent } from './product-information.component';

describe('ProductInformationComponent', (): void => {
    let component: ProductInformationComponent;
    let fixture: ComponentFixture<ProductInformationComponent>;

    beforeEach(waitForAsync((): void => {
        TestBed.configureTestingModule({
            declarations: [ ProductInformationComponent ]
        }).compileComponents();
    }));

    beforeEach((): void => {
        fixture = TestBed.createComponent(ProductInformationComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', (): void => {
        expect(component).toBeTruthy();
    });
});

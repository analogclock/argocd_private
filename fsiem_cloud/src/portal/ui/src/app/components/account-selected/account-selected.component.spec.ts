//  Angular imports
import { ActivatedRoute } from '@angular/router';
import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
//  Application imports
import { AccountSelectedComponent } from './account-selected.component';
import { WINDOW_TOKEN } from 'app/window-token';
import { WindowMock } from 'app/window-mock';
//  Third party imports
import { CookieModule } from 'ngx-cookie';
import { of } from 'rxjs';

const data: string = 'data=%22aF9rZXk9JTdCJTIyc291c' +
    'mNlX2FwcCUyMiUzQSUyMlN1cHBvcnRTaXRlJTIyJTJDJTIyY' +
    'WNjb3VudF9pZCUyMiUzQSUyMjg3NjE0NSUyMiUyQyUyMnVzZX' +
    'JfaWQlMjIlM0ElMjIwJTIyJTJDJTIydXNlcl9mdWxsYWNjZXNz' +
    'JTIyJTNBJTIyVHJ1ZSUyMiUyQyUyMnBhcnRuZXJfaWQlMjIlM0E' +
    'lMjIlMjIlMkMlMjJ2aXNpdGVkX3NpdGVzJTIyJTNBJTVCJTdCJT' +
    'IyYXBwX25hbWUlMjIlM0ElMjJTdXBwb3J0U2l0ZSUyMiUyQyUyMm' +
    'xhc3RfdXJsJTIyJTNBJTIyaHR0cCUzQSUyRiUyRjE3Mi4zMC4zOC4' +
    'xMDAlMkZSZWdpc3RyYXRpb25EZXYlMkZNYWluLmFzcHglMjIlN0QlNUQlN0Q=%22';

describe('AccountSelectedComponent', (): void => {
    let component: AccountSelectedComponent;
    let fixture: ComponentFixture<AccountSelectedComponent>;

    beforeEach(waitForAsync((): void => {
        TestBed.configureTestingModule({
            imports: [
                CookieModule.forRoot()
            ],
            declarations: [
                AccountSelectedComponent
            ],
            providers: [
                {
                    provide: ActivatedRoute, useValue: {
                        queryParamMap: of(data)
                    }
                },
                { provide: WINDOW_TOKEN, useClass: WindowMock }
            ]
        })
            .compileComponents();
    }));

    beforeEach((): void => {
        fixture = TestBed.createComponent(AccountSelectedComponent);
        component = fixture.componentInstance;
    });

    it('should create', (): void => {
        expect(component).toBeTruthy();
    });
});

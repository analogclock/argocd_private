//  Angular imports
import { HttpResponse } from '@angular/common/http';
//  Application imports
import { RAccount } from 'app/records/account.record';
//  Third party imports
import { BehaviorSubject, Observable, of } from 'rxjs';

export class UserServiceMock {

    public accountSelected$: BehaviorSubject<RAccount> = new BehaviorSubject<RAccount>(new RAccount());
    public isAuthenticated: boolean = false;

    public get isAuthenticated$(): Observable<boolean> {
        if (!this.isAuthenticated) {
            return of(false);
        } else {
            return of(true);
        }
    }

    public getAccounts(): Observable<HttpResponse<Array<RAccount>> | Array<RAccount>> {
        return of(new HttpResponse<Array<RAccount>>({body: []}));
    }

    public getAccount(): Observable<HttpResponse<RAccount> | RAccount> {
        return of(null);
    }

    public getEmail(): Observable<string> {
        return of('fake@e.mail');
    }

    public setAuthenticated(): void { }

    public clearAuthenticated(): void { }
}

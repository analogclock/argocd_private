//  Angular imports
import { Injectable } from '@angular/core';
//  Application imports
import { BaseProvisioningService } from './base-provisioning.service';
import { Endpoints } from './endpoints';
import { RAccount } from 'app/records/account.record';
import { RAccountDetails } from 'app/records/account-details.record';
//  Third party imports
import { BehaviorSubject, Observable, of } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class UserService extends BaseProvisioningService {

    public accountSelected$: BehaviorSubject<RAccount> = new BehaviorSubject<RAccount>(null);
    public isAuthenticated$: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
    public userId$: BehaviorSubject<string> = new BehaviorSubject<string>(null);

    public getAccount(accountId: number, userId: number): Observable<RAccount> {
        // check if account id is 0 and don't even call the API
        if (accountId === 0) { return of(null); }
        return this.apiGet<RAccount>(
            `${Endpoints.USER}/${accountId}/${!!userId ? userId : ''}`,
            RAccount
        ) as Observable<RAccount>;
    }

    public getAccounts(observeResponse?: boolean): Observable<Array<RAccountDetails>> {
        return this.apiGet<RAccountDetails>(
            Endpoints.USER,
            RAccountDetails,
            observeResponse
        ) as Observable<Array<RAccountDetails>>;
    }

    public authorise(): Observable<boolean> {
        return this.apiHead(Endpoints.USER);
    }

    public setAuthenticated(): void {
        this.isAuthenticated$.next(true);
    }

    public setGlobalUserId(userId: string): void {
        if(!!userId){
            this.userId$.next(userId);
        }
    }

    public clearAuthenticated(): void {
        this.isAuthenticated$.next(false);
    }
}

//  Angular imports
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
//  Application imports
import { ApplicationRoute } from 'app/models/application-route';
import { HKeyManagerService } from 'app/services/hkey-manager.service';
import { RAccount } from 'app/records/account.record';
import { RAccountDetails } from 'app/records/account-details.record';
import { RHKeyData } from 'app/records/h-key-data.record';
import { UserService } from 'app/services/user.service';
//  Third party imports
import { first } from 'rxjs/operators';

@Component({
    selector: 'zf-account-selection',
    templateUrl: './account-selection.component.html',
    styleUrls: ['./account-selection.component.scss']
})
export class AccountSelectionComponent implements OnInit {
    public showPartialCreatedAccountInfo: boolean = false;
    public accounts: Array<RAccountDetails>;

    constructor(
        private router: Router,
        private userService: UserService,
        private hKeyManagerService: HKeyManagerService
    ) { }

    public ngOnInit(): void {
        this.userService.accountSelected$
            .pipe(
                first()
            )
            .subscribe(
                (account: RAccount): void => {
                    if (account?.details) {
                        this.setSelectedAccount(account);
                    } else {
                        this.loadAccounts();
                    }

                }
            );
    }

    public pickAccount(accountDetails: RAccountDetails): void {
        this.accounts = null;
        this.userService.getAccount(accountDetails.accountId, accountDetails.userId)
            .subscribe(
                (account: RAccount): void => this.setSelectedAccount(account)
            );
    }

    private loadAccounts(defaultAccount?: RAccount): void {
        this.userService.getAccounts()
            .subscribe(
                (accounts: Array<RAccountDetails>): void => {
                    // if there are no accounts, show partial message
                    if (!!accounts && accounts.length === 0) {
                        this.showPartialCreatedAccountInfo = true;
                        // pick the only account
                    } else if (!!accounts && accounts.length === 1) {
                        if (!defaultAccount || accounts[0].accountId !== defaultAccount.details.accountId) {
                            this.pickAccount(accounts[0]);
                        } else {
                            this.setSelectedAccount(defaultAccount);
                        }
                        // let user choose from multiple accounts
                    } else {
                        this.accounts = accounts.sort((a: RAccountDetails, b: RAccountDetails) =>
                            Number(b.isMasterUser) - Number(a.isMasterUser)
                        );
                    }
                }
            );
    }

    private completeAndStore(account: RAccountDetails): void {
        const hKeyDataPartial: Partial<RHKeyData> = RHKeyData.partialFromAccount(account);
        const storedHKey: RHKeyData = this.hKeyManagerService.get();
        const hKeyData: RHKeyData = RHKeyData.complete(hKeyDataPartial, storedHKey);
        this.hKeyManagerService.store(hKeyData);
    }

    private setSelectedAccount(account: RAccount): void {
        this.completeAndStore(account.details);
        this.userService.accountSelected$.next(account);
        this.router.navigateByUrl(ApplicationRoute.ENTITLEMENTS);
    }
}

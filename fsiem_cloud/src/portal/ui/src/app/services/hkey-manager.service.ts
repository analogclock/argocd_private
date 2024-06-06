//  Angular imports
import { Injectable } from '@angular/core';
//  Third party imports
import { CookieService } from 'ngx-cookie';
import { GenericDeserialize, Serialize } from 'cerialize';
import { RHKeyData } from 'app/records/h-key-data.record';

@Injectable({
    providedIn: 'root'
})
export class HKeyManagerService {

    private key: string;

    constructor(
        private cookieService: CookieService
    ) {
        // look up h-keys from cookies
        const hKeys: Array<string> = Object.keys(this.cookieService.getAll())
            .filter(
                (key: string): boolean => key.startsWith('hKey')
            );

        // if it's unambiguous, set its key as service key
        if (hKeys.length === 1) {
            this.key = hKeys[0];
        }
    }

    public store(hKeyData: RHKeyData): void {
        this.key = `hKey-${hKeyData.accountId}`;
        this.cookieService.putObject(this.key, Serialize(hKeyData), {
            expires: new Date(Date.now() + 60 * 60 * 1000),
            secure: true
        });
    }

    public get(): RHKeyData {
        return GenericDeserialize(this.cookieService.getObject(this.key), RHKeyData);
    }

    public delete(): void {
        this.cookieService.remove(this.key);
    }
}

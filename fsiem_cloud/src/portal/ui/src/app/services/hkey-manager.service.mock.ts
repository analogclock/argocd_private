//  Application imports
import { RHKeyData } from 'app/records/h-key-data.record';

export class HKeyManagerServiceMock {
    public store(): void {
    }
    public get(): RHKeyData {
        return new RHKeyData();
    }
    public delete(): void {
    }
}

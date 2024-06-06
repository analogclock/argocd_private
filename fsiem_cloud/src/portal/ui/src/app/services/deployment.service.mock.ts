//  Application imports
import { RDeployment } from 'app/records/deployment.record';
//  Third party imports
import { Observable, of } from 'rxjs';

export class DeploymentServiceMock {
    public getDeployments(): Observable<Array<RDeployment>> {
        return of([]);
    }

    public getDeployment(): Observable<RDeployment> {
        return of();
    }

    public deleteDeployment(): Observable<boolean> {
        return of();
    }

    public activate(): Observable<string> {
        return of();
    }
}

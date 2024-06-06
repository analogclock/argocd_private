import { Pipe, PipeTransform } from '@angular/core';
import { RDeploymentType } from 'app/records/deployment-type.record';

@Pipe({
    name: 'deploymentType'
})
export class DeploymentTypePipe implements PipeTransform {

    public transform(value: string): string {
        if (value) {
            const dType = RDeploymentType.fromStored.get(value);
            const deploymentType = RDeploymentType.toDisplay.get(dType);
            return deploymentType;
        }

        return;
    }

}

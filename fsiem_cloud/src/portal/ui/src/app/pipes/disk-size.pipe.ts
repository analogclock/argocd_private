import { Pipe, PipeTransform } from '@angular/core';
import { RDeploymentType } from 'app/records/deployment-type.record';
import { DiskCalculator } from './disk-calculator';

@Pipe({
    name: 'diskSize'
})
export class DiskSizePipe implements PipeTransform {

    public transform(bytes: number|string, decimals: number): string {
        return DiskCalculator.toHuman(bytes, decimals);
    }
}

import { Pipe, PipeTransform } from '@angular/core';
import { RTerm } from 'app/records/entitlement.record';
import { DiskCalculator } from './disk-calculator';

@Pipe({
    name: 'SKU'
})
export class SKUDisplayPipe implements PipeTransform {

    public transform(value: RTerm, args?: any): string {
        if (value && args) {
            if (args === 'compute') {
                return `${value?.quantity * 10 || 0} FCU (${value?.quantity || 0} x 10 FCU)`;
            } else if (args === 'online' || args === 'archive') {
                if (value?.quantity === 0) {
                    return '0 (0 x 500GB)';
                }
                return `${DiskCalculator.toHuman(value?.quantity * (500 * 1000 * 1000 * 1000), 1)} (${value?.quantity} x 500GB)`;
            }
        }

        return '';
    }
}

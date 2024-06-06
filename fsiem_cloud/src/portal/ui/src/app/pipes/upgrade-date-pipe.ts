import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
    name: 'upgradeDate'
})
export class UpgradeDatePipe implements PipeTransform {

    public transform(value: string, args?: any): string {
        if (value && args) {
            // has 6 chars (+08:00, +00:00, -09:00)
            if (args === 'offset') {
                return `${value.slice(-6)}`;
            }

            if (args === 'hour' || args === 'day') {

                const split = value.split('T');

                switch(args) {
                    case 'hour':
                        return split[1].slice(0, 5);
                    case 'day':
                        return split[0];
                }
            }
        }

        return '';
    }
}

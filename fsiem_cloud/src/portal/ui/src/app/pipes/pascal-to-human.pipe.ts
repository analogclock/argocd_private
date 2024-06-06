import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
    name: 'pascalToHuman'
})
export class PascalToHumanPipe implements PipeTransform {

    public transform(value: string): string {
        if (value) {
            return value.pascalToHumanReadable();
        }

        return '';
    }
}

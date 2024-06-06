import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
    name: 'csv'
})
export class CsvDisplayPipe implements PipeTransform {

    public transform(value: string): string {
        if (value) {
            return value.replaceAll(',', ', ');
        }

        return;
    }

}

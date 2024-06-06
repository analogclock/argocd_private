import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
    name: 'errorText'
})
export class ErrorDisplayTextPipe implements PipeTransform {

    public transform(value: string | boolean): string {
        if (typeof value === 'string') {
            return value;
        }

        // else we don't want to show anything, but we still need to highlight
        return '';
    }
}

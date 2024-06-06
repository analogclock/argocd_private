import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
    name: 'url'
})
export class UrlDisplayPipe implements PipeTransform {

    public transform(value: string): string {
        if (value) {
            return value.endsWith('.') ?
                value.stripLast().stripProtocol() :
                value.stripProtocol();
        }

        return;
    }
}

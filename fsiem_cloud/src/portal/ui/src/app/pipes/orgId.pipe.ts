import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
    name: 'orgId'
})
export class OrgIdPipe implements PipeTransform {

    public transform(value: number): string {
        if (value === -1) {
            return 'ALL';
        }

        return value.toString();
    }
}

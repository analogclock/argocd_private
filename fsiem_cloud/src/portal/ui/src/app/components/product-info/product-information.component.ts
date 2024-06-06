//  Angular imports
import { Component } from '@angular/core';
import { environment } from 'environments/environment';

@Component({
    selector: 'zf-product-information',
    templateUrl: './product-information.component.html',
    styleUrls: ['./product-information.component.scss']
})
export class ProductInformationComponent {

    public readonly productName: string = environment.productName;

    constructor() { }

}

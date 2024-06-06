//  Angular imports
import { ElementRef } from '@angular/core';

export class ZFDropdownComponentMock {
    public input: ElementRef = new ElementRef(document.createElement('input'));
    public resetDropDownElement(): void { }
}

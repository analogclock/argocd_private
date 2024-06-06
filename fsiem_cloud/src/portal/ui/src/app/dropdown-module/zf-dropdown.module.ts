//  Angular imports
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NgModule } from '@angular/core';
//  Application imports
import { ZFDropdownComponent } from './components/zf-dropdown.component';

@NgModule({
    declarations: [
        ZFDropdownComponent
    ],
    imports: [
        CommonModule,
        FormsModule
    ],
    exports: [
        ZFDropdownComponent
    ]
})
export class ZFDropdownModule { }

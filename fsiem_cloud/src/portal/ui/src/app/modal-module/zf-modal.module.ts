//  Angular imports
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NgModule } from '@angular/core';
//  Application imports
import { ZFModalComponent } from './zf-modal.component';

@NgModule({
    declarations: [
        ZFModalComponent
    ],
    imports: [
        CommonModule,
        FormsModule
    ],
    exports: [
        ZFModalComponent
    ]
})
export class ZFModalModule { }

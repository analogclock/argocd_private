//  Angular imports
import { Component, ElementRef, EventEmitter, Input, Output, ViewChild } from '@angular/core';
//  Application imports
import { Utils } from 'app/utils';

@Component({
    selector: 'zf-modal',
    templateUrl: './zf-modal.component.html',
    styleUrls: ['./zf-modal.component.scss']
})
export class ZFModalComponent {

    public visible: boolean = false;
    public readonly duration: number = 500;

    public get footerPresent(): boolean {
        return !!this.footerContent.nativeElement.innerHTML.length;
    }

    @Input()
    public id: string;

    @Output()
    public onClose: EventEmitter<void> = new EventEmitter<void>();

    @ViewChild('footer', { static: true }) private footerContent: ElementRef;

    constructor() { }

    public toggle(): void {
        if (this.visible) {
            this.onClose.emit();
            setTimeout((): void => {
                this.visible = false;
                document.body.style.pointerEvents = 'auto';
                document.body.style.overflow = 'auto';
            }, this.duration);
        } else {
            this.visible = true;
            document.body.style.pointerEvents = 'none';
            document.body.style.overflow = 'hidden';
        }
        Utils.animate(document.body.classList, this.duration);
    }
}

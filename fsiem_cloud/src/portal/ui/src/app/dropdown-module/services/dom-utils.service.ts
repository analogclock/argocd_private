//  Angular imports
import { Injectable } from '@angular/core';
//  Application imports
import { DOMEvent } from '../models/dom-event';
import { DOMEventType } from '../models/dom-event-type';
//  Third party imports
import { DOM } from 'rx-dom';
import { fromEvent, Observable } from 'rxjs';
import { Subject } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class DOMUtilsService {

    public domChanged$: Subject<DOMEvent> = new Subject<DOMEvent>();
    private scroll$: Observable<UIEvent> = DOM.scroll(document.body, null, true) as any;
    private windowScroll$: Observable<UIEvent> = fromEvent(window, 'scroll') as any;
    private bodyClick$: Observable<UIEvent> = DOM.click(document.body) as any;
    private windowResize$: Observable<UIEvent> = fromEvent(window, 'resize') as any;

    constructor() {
        this.initialiseListeners();
    }

    // cross-browser way to get styling rule for element
    public getStyle(elem: any, slugCSS: string): string {

        try {
            // IE
            if (!!elem.currentStyle) {
                const camelCSS: string = slugCSS.replace(
                    /-([a-z])/g, function (match: string): string { return match[1].toUpperCase(); }
                );
                return elem.currentStyle[camelCSS];

            // other browsers
            } else {
                return document.defaultView.getComputedStyle(elem, null).getPropertyValue(slugCSS);
            }
        } catch (e) {
            return null;
        }
    }

    private initialiseListeners(): void {
        this.scroll$.subscribe(
            (scroll: UIEvent): void => this.domChanged$.next(new DOMEvent(DOMEventType.SCROLL, scroll.target))
        );
        this.windowScroll$.subscribe(
            (): void => this.domChanged$.next(new DOMEvent(DOMEventType.SCROLL, window))
        );
        this.bodyClick$.subscribe(
            (click: UIEvent): void => this.domChanged$.next(new DOMEvent(DOMEventType.CLICK, click.target))
        );
        this.windowResize$.subscribe(
            (): void => this.domChanged$.next(new DOMEvent(DOMEventType.RESIZE, window))
        );
    }
}

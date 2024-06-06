//  Application imports
import { DOMEvent } from '../models/dom-event';
import { DOMEventType } from '../models/dom-event-type';
//  Third party imports
import { Subject } from 'rxjs';

export class DOMUtilsServiceMock {
    public domChanged$: Subject<DOMEvent> = new Subject<DOMEvent>();

    public getStyle(): string {
        return '';
    }

    public fakeScroll(): void {
        this.domChanged$.next(new DOMEvent(DOMEventType.SCROLL, {} as EventTarget));
    }

    public fakeResize(): void {
        this.domChanged$.next(new DOMEvent(DOMEventType.RESIZE, {} as EventTarget));
    }
}

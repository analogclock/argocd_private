//  Application imports
import { DOMEventType } from './dom-event-type';

export class DOMEvent {
    constructor (
        public type: DOMEventType,
        public target: EventTarget) { }
}

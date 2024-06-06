//  Angular imports
import { inject, TestBed } from '@angular/core/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';
//  Application imports
import { DOMEvent } from '../models/dom-event';
import { DOMEventType } from '../models/dom-event-type';
import { DOMUtilsService } from './dom-utils.service';
//  Third party imports
import { of } from 'rxjs';

describe('DOMUtilsService', (): void => {

    let testElement: HTMLElement;
    let testStyle: HTMLElement;

    beforeEach((): void => {
        TestBed.configureTestingModule({
            providers: [
                DOMUtilsService
            ],
            schemas: [ NO_ERRORS_SCHEMA ]
        });

        // create test div
        const div: HTMLDivElement = document.createElement('div');
        div.id = 'test-element';
        div.className = 'test-element';
        div.innerText = 'Test Element';
        // create test link
        const link: HTMLAnchorElement = document.createElement('a');
        link.href = 'http://pointing/nowhere';
        link.id = 'test-link';
        // create test style
        const style: HTMLStyleElement = document.createElement('style');
        style.id = 'test-style';
        style.appendChild(document.createTextNode('#test-element { min-width: 12px; }'));
        // append test elements
        div.appendChild(link);
        document.head.appendChild(style);
        document.body.appendChild(div);
    });

    afterEach((): void => {
        testElement = document.getElementById('test-element');
        testStyle = document.getElementById('test-style');
        testElement.parentElement.removeChild(testElement);
        testStyle.parentElement.removeChild(testStyle);
    });

    it('should create', inject([DOMUtilsService], (service: DOMUtilsService): void => {
        expect(service).toBeTruthy();
    }));

    it('should listen to scroll events', inject([DOMUtilsService], (service: DOMUtilsService): void => {
        spyOn(service.domChanged$, 'next');
        service['scroll$'] = of({ target: testElement }) as any;
        service['initialiseListeners']();
        expect(service.domChanged$.next).toHaveBeenCalledWith(new DOMEvent(DOMEventType.SCROLL, testElement));
    }));

    it('should listen to window scroll events', inject([DOMUtilsService], (service: DOMUtilsService): void => {
        spyOn(service.domChanged$, 'next');
        service['windowScroll$'] = of({}) as any;
        service['initialiseListeners']();
        expect(service.domChanged$.next).toHaveBeenCalledWith(new DOMEvent(DOMEventType.SCROLL, window));
    }));

    it('should listen to body click events', inject([DOMUtilsService], (service: DOMUtilsService): void => {
        spyOn(service.domChanged$, 'next');
        service['bodyClick$'] = of({ target: testElement }) as any;
        service['initialiseListeners']();
        expect(service.domChanged$.next).toHaveBeenCalledWith(new DOMEvent(DOMEventType.CLICK, testElement));
    }));

    it('should listen to window resize events', inject([DOMUtilsService], (service: DOMUtilsService): void => {
        spyOn(service.domChanged$, 'next');
        service['windowResize$'] = of({}) as any;
        service['initialiseListeners']();
        expect(service.domChanged$.next).toHaveBeenCalledWith(new DOMEvent(DOMEventType.RESIZE, window));
    }));

    it('should get style for Internet Explorer', inject([DOMUtilsService], (service: DOMUtilsService): void => {
        testElement = { currentStyle: { minWidth: '12px' } } as any as HTMLElement;
        expect(service.getStyle(testElement, 'min-width')).toBe('12px');
    }));

    it('should get style for other browsers', inject([DOMUtilsService], (service: DOMUtilsService): void => {
        testElement = document.getElementById('test-element');
        expect(service.getStyle(testElement, 'min-width')).toBe('12px');
    }));

    it('should not get style when it is impossible', inject([DOMUtilsService], (service: DOMUtilsService): void => {
        testElement = {} as HTMLElement;
        expect(service.getStyle(testElement, 'min-width')).toBeNull();
    }));
});

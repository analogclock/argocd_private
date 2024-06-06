//  Angular imports
import { By } from '@angular/platform-browser';
import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { FormsModule } from '@angular/forms';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { SimpleChange } from '@angular/core';
//  Application imports
import { DOMUtilsService } from '../services/dom-utils.service';
import { DOMUtilsServiceMock } from '../mocks/dom-utils.service.mock';
import { Selectable } from '../models/selectable';
import { ZFDropdownComponent } from './zf-dropdown.component';
//  Third party imports
import { Key } from 'ts-key-enum';
import { Observable, of, Subject, Subscription } from 'rxjs';

describe('ZFDropdownComponent', (): void => {
    let component: ZFDropdownComponent;
    let fixture: ComponentFixture<ZFDropdownComponent>;

    beforeEach(waitForAsync((): void => {
        TestBed.configureTestingModule({
            imports: [ FormsModule ],
            declarations: [ ZFDropdownComponent ],
            schemas: [ NO_ERRORS_SCHEMA ],
            providers: [ { provide: DOMUtilsService, useClass: DOMUtilsServiceMock } ]
        }).compileComponents();
    }));

    beforeEach((): void => {
        fixture = TestBed.createComponent(ZFDropdownComponent);
        component = fixture.componentInstance;
        component.inputId = 'test-input';
        component['elements'] = [
            new Selectable('a', 'b', 'c'),
            new Selectable('d', 'e', 'f'),
            new Selectable('g', 'h', 'i')
        ];
        fixture.detectChanges();
    });

    afterEach((): void => {
        component['subscriptions'].forEach(
            (subscription: Subscription): void => subscription.unsubscribe()
        );
    });

    it('should create', (): void => {
        expect(component).toBeTruthy();
    });

    it('should subscribe to clicks and keyups', (): void => {
        expect(component['subscriptions'].length).toBe(2);
    });

    it('should update input value and list', waitForAsync((): void => {
        const display: string = 'wilma';
        const value: string = 'fred';
        const selectable: Selectable = new Selectable(display, value, 'cavemen');
        component['elements'] = [selectable];
        component.value = value;

        component.ngOnChanges({
            elements: new SimpleChange([], [selectable], false),
            value: new SimpleChange('bernie', value, false)
        });

        setTimeout( (): void => {
            expect(component.filterExpression).toEqual(display);
            expect(component.filteredElements.length).toBe(1);
        });

        component.ngOnChanges({});

        setTimeout( (): void => {
            expect(component.filterExpression).toEqual(display);
            expect(component.filteredElements.length).toBe(1);
        });
    }));

    it('should tell if the dropdown is open', (): void => {
        component.open = false;
        expect(component.isOpen()).toBeFalsy();
        component.open = true;
        expect(component.isOpen()).toBeTruthy();
    });

    it('should emit priority string on enter if value matches', (): void => {
        component['priorityStrings'] = ['duMmy-stRing-oNe', 'dUmmY-StrIng-twO'];
        component.input.nativeElement.value = 'DumMy-sTrinG-TWo';
        spyOn(component, 'select');
        spyOn(component['freeHand'], 'emit');
        component['elements'] = [ new Selectable('abcdef'), new Selectable('defghi') ];
        component.filteredElements = [];
        component.enter();
        expect(component.select).not.toHaveBeenCalled();
        expect(component['freeHand'].emit).toHaveBeenCalledWith('dummy-string-two');
    });

    it('should not emit priority string on enter if case sensitive values fail to match', (): void => {
        component['caseSensitive'] = true;
        component['priorityStrings'] = ['dummy-string-one', 'dummy-string-two'];
        component.input.nativeElement.value = 'Dummy-string-two';
        spyOn(component, 'select');
        spyOn(component['freeHand'], 'emit');
        component['elements'] = [ new Selectable('abcdef'), new Selectable('defghi') ];
        component.filteredElements = [];
        component.enter();
        expect(component.select).not.toHaveBeenCalled();
        expect(component['freeHand'].emit).not.toHaveBeenCalled();
    });

    it('should not select on enter if element is not found', (): void => {
        spyOn(component, 'select');
        spyOn(component['freeHand'], 'emit');
        component['elements'] = [ new Selectable('abcdef'), new Selectable('defghi') ];
        component.filteredElements = [];
        component.enter();
        expect(component.select).not.toHaveBeenCalled();
        expect(component['freeHand'].emit).not.toHaveBeenCalled();
    });

    it('should not select on enter if filtered list contains several items', (): void => {
        spyOn(component, 'select');
        spyOn(component['freeHand'], 'emit');
        component['elements'] = [ new Selectable('abcdef'), new Selectable('defghi') ];
        component.filteredElements = [ new Selectable('abcdef'), new Selectable('defghi') ];
        component.enter();
        expect(component.select).not.toHaveBeenCalled();
        expect(component['freeHand'].emit).not.toHaveBeenCalled();
    });

    it('should select on enter element matching the only value of filtered elements', (): void => {
        spyOn(component, 'select');
        spyOn(component['freeHand'], 'emit');
        component['elements'] = [ new Selectable('abcdef'), new Selectable('defghi') ];
        component.filteredElements = [ new Selectable('abcdef') ];
        component.enter();
        expect(component.select).toHaveBeenCalledWith(new Selectable('abcdef'));
        expect(component['freeHand'].emit).not.toHaveBeenCalled();
    });

    it('should select a list item', (): void => {
        spyOn(component['selectElement'], 'emit');

        component.open = true;
        component.select(new Selectable('wilma', 'fred', 'oongaboonga'));
        fixture.detectChanges();

        expect(component.open).toBeFalsy();
        expect(fixture.debugElement.query(By.css('input')).nativeElement.value).toBe('wilma');
        expect(component['selectElement'].emit).toHaveBeenCalledWith('fred');

        component.open = true;
        component.select(new Selectable('wilma', 'fred', 'oongaboonga'), { stopPropagation: (): void => {} } as MouseEvent);
        fixture.detectChanges();
    });

    it('should react to keydowns appropriately', (): void => {
        const enter: KeyboardEvent = { key: Key.Enter, preventDefault: function(): void { } } as any as KeyboardEvent;
        const escape: KeyboardEvent = { key: Key.Escape, preventDefault: function(): void { } } as any as KeyboardEvent;
        const down: KeyboardEvent = { key: Key.ArrowDown, preventDefault: function(): void { } } as any as KeyboardEvent;

        spyOn(component, 'select');
        spyOn(component, 'closeDropdown' as any);
        spyOn(component, 'proceedInList' as any);
        const wilma: Selectable = new Selectable('wilma');
        const fred: Selectable = new Selectable('fred');

        component.onKeydown({} as any, wilma);

        expect(component.select).not.toHaveBeenCalled();
        expect(component['closeDropdown']).not.toHaveBeenCalled();
        expect(component['proceedInList']).not.toHaveBeenCalled();

        component.onKeydown(enter, wilma);
        expect(component.select).toHaveBeenCalledWith(wilma);

        expect(component['closeDropdown']).not.toHaveBeenCalled();
        component.onKeydown(escape, wilma);
        expect(component.open).toBeFalsy();
        expect(component['closeDropdown']).toHaveBeenCalled();

        expect(component['proceedInList']).not.toHaveBeenCalled();
        component.onKeydown(down, fred);
        expect(component['proceedInList']).toHaveBeenCalledWith(down);
    });

    it('should reset dropdown element', (): void => {
        spyOn(component, 'setDimensionsAndPosition' as any);
        spyOn(component, 'closeDropdown' as any);
        spyOn(component, 'openDropdown' as any);
        component.open = true;
        component.dropUp = true;
        component['previousDropUp'] = false;

        component.resetDropDownElement();

        expect(component['setDimensionsAndPosition']).toHaveBeenCalledWith(component['dropDownContainer'].nativeElement);
        expect(component['closeDropdown']).toHaveBeenCalledTimes(1);

        component.open = false;
        component.resetDropDownElement();
        expect(component['closeDropdown']).toHaveBeenCalledTimes(1);
    });

    it('should unsubscribe from listeners', (): void => {
        component.ngOnDestroy();

        component['subscriptions'].forEach(
            (subscription: Subscription): void => expect(subscription.closed).toBeTruthy()
        );

        component['subscriptions'] = [];
        component.ngOnDestroy();

        component['subscriptions'].forEach(
            (subscription: Subscription): void => expect(subscription.closed).toBeTruthy()
        );
    });

    it('should set string value', waitForAsync((): void => {
        component.filterExpression = null;

        component['elements'] = [
            new Selectable('selected display', 1)
        ];
        component.value = '1';
        component['setValue']();
        setTimeout( (): void => {
            expect(component['filterExpression']).toBe('selected display');
        });
    }));

    it('should set false value', waitForAsync((): void => {
        component.filterExpression = null;

        component['elements'] = [
            new Selectable('No', false)
        ];
        (component.value as any) = false;
        component['setValue']();
        setTimeout( (): void => {
            expect(component['filterExpression']).toBe('No');
        });
    }));

    it('should set zero value', waitForAsync((): void => {
        component.filterExpression = null;

        component['elements'] = [
            new Selectable('None', 0)
        ];
        (component.value as any) = 0;
        component['setValue']();
        setTimeout( (): void => {
            expect(component['filterExpression']).toBe('None');
        });
    }));

    it('should set case insensitive value', waitForAsync((): void => {
        component.filterExpression = null;

        component['elements'] = [
            new Selectable('Selected Display', 'Selected Value')
        ];
        component.value = 'selected value';
        component['caseSensitive'] = false;
        component['setValue']();
        setTimeout( (): void => {
            expect(component['filterExpression']).toBe('Selected Display');
        });
    }));

    it('should not set non-existent value', waitForAsync((): void => {
        component.filterExpression = null;

        (component.value as any) = '';
        component['setValue']();
        setTimeout( (): void => {
            expect(component['filterExpression']).toBeNull();
        });
    }));

    it('should set false value', waitForAsync((): void => {
        component.filterExpression = null;

        (component.value as any) = false;
        component['setValue']();
        setTimeout( (): void => {
            expect(component['filterExpression']).toBeNull();
        });
    }));

    it('should initialise the lookup map', (): void => {
        component['elements'].push(
            new Selectable('display', 'value', 'I')
        );
        component['lookupMap'] = {};
        component['initLookupMap']();
        expect(component['lookupMap'].i.length).toBe(2);
    });

    it('should filter list', (): void => {
        spyOn(component, 'closeDropdown' as any);
        expect(component.filteredElements.length).toBe(3);
        component['filterList']('f');
        expect(component.filteredElements.length).toBe(1);
        expect(component['closeDropdown']).not.toHaveBeenCalled();
        component['filterList']('j');
        expect(component['closeDropdown']).toHaveBeenCalled();
    });

    it('should filter by display', (): void => {
        expect(component['filterByDisplay']('a').length).toBe(1);
        expect(component['filterByDisplay']('a')[0].value).toBe('b');
    });

    it('should initialise filtered set', (): void => {
        component.filteredElements = [
            new Selectable('display', 'value')
        ];
        expect(component['initFilteredSet']()).toEqual(new Set<string>(['display']));
    });

    it('should not open dropdown if it is already open', (): void => {
        spyOn(component, 'initDropDownListener' as any);
        component.open = true;
        component['openDropdown']();
        expect(component['initDropDownListener']).not.toHaveBeenCalled();
    });

    it('should not close dropdown if it is already closed', (): void => {
        spyOn(component, 'destroyDropDownListener' as any);
        component.open = false;
        component['closeDropdown']();
        expect(component['destroyDropDownListener']).not.toHaveBeenCalled();
    });

    it('should initialise dropdown listener', waitForAsync((): void => {
        spyOn(component, 'destroyDropDownListener' as any);
        spyOn(component, 'resetDropDownElement');
        component['initDropDownListener']();
        expect(component['destroyDropDownListener']).toHaveBeenCalled();

        component['domUtilsService']['fakeScroll']();
        setTimeout(
            (): void => expect(component.resetDropDownElement).toHaveBeenCalled(),
            component['debounce']
        );
    }));

    it('should calculate dimensions and position', (): void => {
        const sectionGap: number = 16;
        component.dropUp = true;
        component['previousDropUp'] = false;
        spyOn(component, 'closeDropdown' as any);

        component['setDimensionsAndPosition']({ getBoundingClientRect: (): any => ({ top: -10 }) } as HTMLElement );
        expect(component['closeDropdown']).toHaveBeenCalled();
        expect(component['previousDropUp']).toBe(true);
        expect(component['dropUp']).toBe(false);

        component['setDimensionsAndPosition']({ getBoundingClientRect: (): any => ({ top: 10, bottom: 10, width: 30 }) } as HTMLElement );
        expect(component.dropDownMaxHeight).toBe(window.innerHeight - 10 - sectionGap);
        expect(component.dropDownWidth).toBe(30);
    });

    it('should subscribe to editing and not stop edit event propagation without an input value', waitForAsync((): void => {
        const event: KeyboardEvent = { key: Key.Backspace, stopPropagation: (): void => {} } as KeyboardEvent;
        component['keyDown$'] = of(event);
        component.input.nativeElement.value = '';
        spyOn(event, 'stopPropagation');
        component['subscribeToEdit']();
        setTimeout( (): void => {
            expect(event.stopPropagation).not.toHaveBeenCalled();
        });
    }));

    it('should subscribe to editing and not stop other event propagation', waitForAsync((): void => {
        const event: KeyboardEvent = { key: '&', stopPropagation: (): void => {} } as KeyboardEvent;
        component['keyDown$'] = of(event);
        component.input.nativeElement.value = 'some-value';
        spyOn(event, 'stopPropagation');
        component['subscribeToEdit']();
        setTimeout( (): void => {
            expect(event.stopPropagation).not.toHaveBeenCalled();
        });
    }));

    it('should subscribe to editing and stop backspace propagation with input value', waitForAsync((): void => {
        const event: KeyboardEvent = { key: Key.Backspace, stopPropagation: (): void => {} } as KeyboardEvent;
        component['keyDown$'] = of(event);
        component.input.nativeElement.value = 'some-value';
        spyOn(event, 'stopPropagation');
        component['subscribeToEdit']();
        setTimeout( (): void => {
            expect(event.stopPropagation).toHaveBeenCalled();
        });
    }));

    it('should subscribe to editing and stop delete propagation with input value', waitForAsync((): void => {
        const event: KeyboardEvent = { key: Key.Delete, stopPropagation: (): void => {} } as KeyboardEvent;
        component['keyDown$'] = of(event);
        component.input.nativeElement.value = 'some-value';
        spyOn(event, 'stopPropagation');
        component['subscribeToEdit']();
        setTimeout( (): void => {
            expect(event.stopPropagation).toHaveBeenCalled();
        });
    }));

    it('should subscribe to list navigation', waitForAsync((): void => {
        component.open = true;
        let event: KeyboardEvent = { key: Key.ArrowUp, preventDefault: (): void => {} } as KeyboardEvent;
        component['keyDown$'] = of(event);
        spyOn(event, 'preventDefault');
        component['subscribeToListNavigation']();
        setTimeout( (): void => {
            expect(event.preventDefault).toHaveBeenCalled();
        });

        event = { key: Key.ArrowDown, preventDefault: (): void => {} } as KeyboardEvent;
        component['keyDown$'] = of(event);
        spyOn(event, 'preventDefault');
        component['subscribeToListNavigation']();
        setTimeout( (): void => {
            expect(event.preventDefault).toHaveBeenCalled();
        });
    }));

    it('should subscribe to input escape keyup', waitForAsync((): void => {
        spyOn(component, 'closeDropdown' as any);
        component['keyUp$'] = of({ key: Key.Escape } as KeyboardEvent);
        component['subscribeToInputKeyup']();
        setTimeout( (): void => {
            expect(component['closeDropdown']).toHaveBeenCalled();
        }, component['delay']);
    }));

    it('should subscribe to input enter keyup', waitForAsync((): void => {
        spyOn(component, 'closeDropdown' as any);
        spyOn(component['freeHand'], 'emit');
        spyOn(component, 'filterList' as any);
        component.input.nativeElement.value = 'value';
        component['keyUp$'] = of({ key: Key.Enter } as KeyboardEvent);
        component['subscribeToInputKeyup']();
        setTimeout( (): void => {
            expect(component['freeHand'].emit).toHaveBeenCalledWith('value');
            expect(component.input.nativeElement.value).toBe('');
            expect(component['filterList']).toHaveBeenCalledWith(null);
            expect(component['closeDropdown']).toHaveBeenCalled();
        }, component['delay']);
    }));

    it('should subscribe to other input keyups', waitForAsync((): void => {
        spyOn(component, 'openDropdown' as any);
        component['keyUp$'] = of({ key: 'K' } as KeyboardEvent);
        component['subscribeToInputKeyup']();
        setTimeout( (): void => {
            expect(component['openDropdown']).toHaveBeenCalled();
        }, component['delay']);
    }));

    it('should subscribe to arrow input keyups', waitForAsync((): void => {
        spyOn(component, 'openDropdown' as any);
        component['keyUp$'] = of({ key: Key.ArrowLeft } as KeyboardEvent);
        component['subscribeToInputKeyup']();
        setTimeout( (): void => {
            expect(component['openDropdown']).not.toHaveBeenCalled();
        }, component['delay']);
    }));

    it('should filter identical input keyups', waitForAsync((): void => {
        spyOn(component, 'filterList' as any);
        const subject: Subject<KeyboardEvent> = new Subject<KeyboardEvent>();
        component['keyUp$'] = subject.asObservable();
        component['subscribeToInputKeyup']();
        subject.next(({ key: 'A' } as KeyboardEvent));
        component.filterExpression = 'A';
        setTimeout( (): void => {
            expect(component['filterList']).toHaveBeenCalledTimes(1);
            subject.next(({ key: Key.ArrowLeft } as KeyboardEvent));
            setTimeout((): void => {
                expect(component['filterList']).toHaveBeenCalledTimes(1);
            }, component['delay'] + 100);   // add 100ms for extra setTimeout in subscription
        }, component['delay'] + 100);
    }));

    it('should subscribe to input click', (): void => {
        spyOn(component, 'openDropdown' as any);
        component.open = true;
        component['inputClick$'] = of({ } as MouseEvent);
        component['subscribeToInputClick']();
        expect(component['openDropdown']).not.toHaveBeenCalled();
        component.open = false;
        component['inputClick$'] = of({ } as MouseEvent);
        component['subscribeToInputClick']();
        expect(component['openDropdown']).toHaveBeenCalled();
    });

    it('should close dropdown to click outside', (): void => {
        spyOn(component, 'closeDropdown' as any);
        component.open = true;
        component['host'].nativeElement.clickOutside = (): Observable<boolean> => of(false, true);
        component['subscribeToClickOutside']();
        expect(component['closeDropdown']).toHaveBeenCalledTimes(1);
    });

    it('should not close dropdown to click inside', (): void => {
        spyOn(component, 'closeDropdown' as any);
        component.open = true;
        const target: Element = (component['host'].nativeElement as HTMLElement).firstElementChild;
        component['clickOutside$'] = of({ target: target as EventTarget } as MouseEvent);
        component['subscribeToClickOutside']();
        expect(component['closeDropdown']).not.toHaveBeenCalled();
    });

    it('should proceed in list', (): void => {
        spyOn(component, 'focusNext' as any);
        spyOn(component, 'focusPrevious' as any);

        const target: HTMLElement = document.createElement('div');
        component['proceedInList']({
            target,
            key: Key.ArrowDown,
            preventDefault: (): void => {}
        } as any as KeyboardEvent);
        expect(component['focusNext']).toHaveBeenCalledWith(target);

        component['proceedInList']({
            target,
            key: Key.ArrowUp,
            preventDefault: (): void => {}
        } as any as KeyboardEvent);
        expect(component['focusPrevious']).toHaveBeenCalledWith(target);
    });

    it('should focus next when there is next', (): void => {
        const container: HTMLDivElement = document.createElement('div');
        container.appendChild(document.createElement('div'));
        container.appendChild(document.createElement('div'));
        container.appendChild(document.createElement('div'));
        spyOn(container.firstElementChild.nextElementSibling as HTMLElement, 'focus');

        component['focusNext'](container.firstElementChild as HTMLElement);
        expect((container.firstElementChild.nextElementSibling as HTMLElement).focus).toHaveBeenCalled();
    });

    it('should focus next when there is no next', (): void => {
        const container: HTMLDivElement = document.createElement('div');
        container.appendChild(document.createElement('div'));
        container.appendChild(document.createElement('div'));
        container.appendChild(document.createElement('div'));
        spyOn(container.firstElementChild as HTMLElement, 'focus');

        component['focusNext'](container.lastElementChild as HTMLElement);
        expect((container.firstElementChild as HTMLElement).focus).toHaveBeenCalled();
    });

    it('should focus previous when there is previous', (): void => {
        const container: HTMLDivElement = document.createElement('div');
        container.appendChild(document.createElement('div'));
        container.appendChild(document.createElement('div'));
        container.appendChild(document.createElement('div'));
        spyOn(container.lastElementChild.previousElementSibling as HTMLElement, 'focus');

        component['focusPrevious'](container.lastElementChild as HTMLElement);
        expect((container.lastElementChild.previousElementSibling as HTMLElement).focus).toHaveBeenCalled();
    });

    it('should focus previous when there is no previous', (): void => {
        const container: HTMLDivElement = document.createElement('div');
        container.appendChild(document.createElement('div'));
        container.appendChild(document.createElement('div'));
        container.appendChild(document.createElement('div'));
        spyOn(container.lastElementChild as HTMLElement, 'focus');

        component['focusPrevious'](container.firstElementChild as HTMLElement);
        expect((container.lastElementChild as HTMLElement).focus).toHaveBeenCalled();
    });
});

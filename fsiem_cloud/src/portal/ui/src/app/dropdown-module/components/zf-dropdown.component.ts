//  Angular imports
import {
    AfterContentInit,
    Component,
    ContentChild,
    ElementRef,
    EventEmitter,
    Input,
    OnChanges,
    OnDestroy,
    Output,
    QueryList,
    SimpleChanges,
    TemplateRef,
    ViewChild,
    ViewChildren
} from '@angular/core';
//  Application imports
import { DOMEvent } from '../models/dom-event';
import { DOMEventType } from '../models/dom-event-type';
import { DOMUtilsService } from '../services/dom-utils.service';
import { Selectable } from '../models/selectable';
//  Third party imports
import { debounceTime, distinctUntilChanged, filter, map, takeWhile, tap } from 'rxjs/operators';
import { fromEvent, Observable, Subscription } from 'rxjs';
import { Key } from 'ts-key-enum';

const sectionGap: number = 16;

(HTMLElement.prototype as any).clickOutside =
    function (whileCondition: () => boolean, filters: Array<() => boolean> = []): Observable<boolean> {
        let clickOutside$: Observable<Event> = fromEvent(document, 'click').pipe(
            takeWhile(whileCondition)
        );

        filters.forEach(
            (filterFunction: () => boolean): Observable<Event> => clickOutside$ = clickOutside$.pipe(
                filter(filterFunction)
            )
        );

        return clickOutside$
            .pipe(
                map(
                    (event: MouseEvent): boolean => !this.contains(event.target)
                )
            );
    };

@Component({
    selector: 'zf-dropdown',
    templateUrl: './zf-dropdown.component.html',
    styleUrls: ['./zf-dropdown.component.scss']
})
export class ZFDropdownComponent implements AfterContentInit, OnChanges, OnDestroy {

    // Bind droped down HTML component with following properties
    public dropDownWidth: number;
    public dropDownMaxHeight: number;
    public visibility: 'hidden' | 'visible' = 'hidden';

    // dropdown elements after filtering
    public filteredElements: Array<Selectable>;
    // search expression to match with elements
    public filterExpression: string;
    public open: boolean = false;

    @ViewChild('input', { static: true })
    public input: ElementRef;
    // id for the input
    @Input()
    public inputId: string = '';
    // placeholder text for the input
    @Input()
    public placeholder: string;
    // whether the input is required
    @Input()
    public required: boolean = false;
    // whether the input is disabled
    @Input()
    public disabled: boolean = false;
    // whether contents should be hidden
    @Input()
    public hidden: boolean = false;
    // initial value
    @Input()
    public value: any;

    @Input()
    public maxHeight: number = null;
    // transcluded template to be rendered
    @ContentChild('zfDropdownElementTemplate', { static: false })
    public dropdownElementTemplate: TemplateRef<any>;

    // dropdown elements before filtering
    @Input()
    public elements: Array<Selectable> = [];

    private readonly delay: number = 100;

    // outermost div
    @ViewChild('host', { static: false })
    private host: ElementRef;
    // DOM representation of elements
    @ViewChildren('filteredDOMElement')
    private filteredDOMElements: QueryList<ElementRef>;

    @Input()
    private caseSensitive: boolean = false;
    // an array of strings that, should the input value match any of them, take precedence over list values
    @Input()
    private priorityStrings: Array<string> = [];
    @Output()
    private selectElement: EventEmitter<any> = new EventEmitter<any>();
    @Output()
    private freeHand: EventEmitter<string> = new EventEmitter<string>();
    private keyDown$: Observable<KeyboardEvent>;
    private keyUp$: Observable<KeyboardEvent>;
    private inputClick$: Observable<MouseEvent>;
    private subscriptions: Array<Subscription> = [];
    // helper map for efficient lookup
    private lookupMap: { [key: string]: Selectable[] } = {};
    // delay before rerendering dropdown
    private readonly debounce: number = 200;
    private domChangeSubscription: Subscription;

    constructor(
        private dropDownContainer: ElementRef,
        private domUtilsService: DOMUtilsService
    ) { }

    public ngAfterContentInit(): void {
        this.initLookupMap();
        this.filterList(null);
        this.keyDown$ = fromEvent(this.input.nativeElement, 'keydown');
        this.keyUp$ = fromEvent(this.input.nativeElement, 'keyup');
        this.inputClick$ = fromEvent(this.input.nativeElement, 'click');
        this.subscriptions.push(this.subscribeToInputKeyup());
        this.subscriptions.push(this.subscribeToInputClick());
    }

    public ngOnChanges(changes: SimpleChanges): void {
        if (!!changes.elements) {
            this.filterList(null);
        }
        if (!!changes.value) {
            this.setValue();
        }
    }

    public isOpen(): boolean {
        return this.open;
    }

    public enter(): void {
        // check for priority string
        const inputValue: string = this.caseSensitive ? this.input.nativeElement.value : this.input.nativeElement.value.toLowerCase();
        const priorityString: string = this.priorityStrings.map(
            (priority: string): string => this.caseSensitive ? priority : priority.toLowerCase()
        ).find(
            (priority: string): boolean => priority === inputValue
        );

        if (!!priorityString) {
            this.freeHand.emit(priorityString);

            // check if elements are filtered to a single one
        } else if (this.filteredElements.length === 1) {
            this.select(this.filteredElements[0]);
        }
    }

    public select(selectedElement: Selectable, event: MouseEvent = null): void {
        if (!!event) { event.stopPropagation(); }
        this.closeDropdown();
        this.input.nativeElement.value = selectedElement.display;
        this.filterList(null);
        this.selectElement.emit(selectedElement.value);
    }

    public onKeydown(event: KeyboardEvent, item: Selectable): void {
        if (!event.key || ![Key.Enter, Key.Escape, Key.ArrowUp, Key.ArrowDown].includes(event.key as Key)) {
            return;
        }
        event.preventDefault();

        if (event.key === Key.Enter) {
            this.select(item);
        } else if (event.key === Key.Escape) {
            this.closeDropdown();
            this.input.nativeElement.focus();
        } else {
            this.proceedInList(event);
        }
    }

    public resetDropDownElement(): void {
        const container: HTMLElement = this.dropDownContainer.nativeElement;

        this.setDimensionsAndPosition(container);

        if (this.open) {
            this.closeDropdown();
            setTimeout((): void =>
                this.openDropdown()
            );
        }
    }

    public ngOnDestroy(): void {
        this.destroyDropDownListener();
        if (!!this.subscriptions && !!this.subscriptions.length) {
            this.subscriptions.forEach(
                (subscription: Subscription): void => subscription.unsubscribe()
            );
        }
    }

    // filtering

    private setValue(): void {
        setTimeout((): void => {
            if (!!this.value || this.value === false || this.value === 0) {
                const foundElement: Selectable = this.elements.find(
                    (element: Selectable): boolean => {
                        if (!this.caseSensitive && typeof this.value === 'string' && typeof element.value === 'string') {
                            return this.value.toLowerCase() === element.value.toLowerCase();
                        } else {
                            return this.value.toString() === element.value.toString();
                        }
                    }
                );
                if (!!foundElement) { this.filterExpression = foundElement.display; }
            }
        });
    }

    private initLookupMap(): void {
        this.elements.forEach(
            (element: Selectable): void => element.searchables
                .map((searchable: string): string => searchable.toLowerCase())
                .forEach((searchable: string): any =>
                    searchable in this.lookupMap ?
                        this.lookupMap[searchable].push(element) :
                        this.lookupMap[searchable] = [element]));
    }

    private filterList(filterExpression: string): void {
        if (!filterExpression) {
            this.filteredElements = this.elements;
            return;
        }
        // convert search expression to lowercase
        const filterExpressionLower: string = filterExpression.toLowerCase();
        // look up elements by their display value
        this.filteredElements = this.filterByDisplay(filterExpressionLower);
        // create set to store used display values
        const filteredSet: Set<string> = this.initFilteredSet();
        // look up elements by their searchables
        this.filterBySearchables(filterExpressionLower, filteredSet);

        if (!this.filteredElements.length) {
            this.closeDropdown();
        }
    }

    private filterByDisplay(filterExpressionLower: string): Array<Selectable> {
        return this.elements
            .filter(
                (dropdownElement: Selectable): boolean => dropdownElement.display.toLowerCase().indexOf(filterExpressionLower) > -1
            )
            .map(
                (dropdownElement: Selectable): Selectable => new Selectable(
                    dropdownElement.display,
                    dropdownElement.value,
                    ...[]
                )
            );
    }

    private initFilteredSet(): Set<string> {
        const set: Set<string> = new Set();
        this.filteredElements.map(
            (filteredElement: Selectable): any => filteredElement.display
        ).forEach(
            (display: string): Set<string> => set.add(display)
        );
        return set;
    }

    private filterBySearchables(filterExpressionLower: string, filteredSet: Set<string>): void {
        Object.keys(this.lookupMap)
            .filter((key: string): boolean => key.indexOf(filterExpressionLower) > -1)
            .forEach((key: string): void => {
                const filteredElements: Array<Selectable> = this.lookupMap[key].map(
                    (filteredElement: Selectable): Selectable => new Selectable(
                        filteredElement.display,
                        filteredElement.value,
                        key
                    )
                ).filter((el: Selectable): boolean => !filteredSet.has(el.display));
                this.filteredElements = [...this.filteredElements, ...filteredElements];
            });
    }

    // open, close, orientation and size

    private openDropdown(): void {
        if (!!this.filteredElements.length && !this.open) {
            this.open = true;
            this.visibility = 'visible';
            this.initDropDownListener();
            this.setDimensionsAndPosition(this.dropDownContainer.nativeElement);
            this.subscriptions.push(this.subscribeToClickOutside());
            this.subscriptions.push(this.subscribeToEdit());
            this.subscriptions.push(this.subscribeToListNavigation());
        }
    }

    private closeDropdown(): void {
        if (this.open) {
            this.open = false;
            this.visibility = 'hidden';
            this.destroyDropDownListener();
        }
    }

    // listen to DOM changes and change status accordingly
    private initDropDownListener(): void {
        this.destroyDropDownListener(); // make sure it is not re-hooked
        this.domChangeSubscription = this.domUtilsService.domChanged$
            .pipe(
                filter((domEvent: DOMEvent): boolean => // ignore irrelevant events
                    domEvent.type === DOMEventType.RESIZE ||
                    domEvent.type === DOMEventType.SCROLL
                ),
                debounceTime(this.debounce)
            )
            .subscribe((): void => this.resetDropDownElement());
    }

    private destroyDropDownListener(): void {
        if (!!this.domChangeSubscription) {
            this.domChangeSubscription.unsubscribe();
        }
    }

    private setDimensionsAndPosition(container: HTMLElement): void {
        // calculate dimensions
        const before: number = container.getBoundingClientRect().top;
        const after: number = window.innerHeight - container.getBoundingClientRect().bottom;

        if (before < 0) {
            // close menu if container is under menu container
            this.closeDropdown();
        }

        // set calculated values
        this.dropDownMaxHeight = this.maxHeight
            ? this.maxHeight
            : Math.max(before, after) - sectionGap; // minus some breathing space (more than horizontal scrollbar 15 / 17px)
        this.dropDownWidth = container.getBoundingClientRect().width;
    }

    private subscribeToEdit(): Subscription {
        return this.keyDown$.
            subscribe(
                (event: KeyboardEvent): void => {
                    // allow normal editing when there is content
                    // otherwise let the event propagate
                    // and parent components deal with it
                    if ((event.key === Key.Delete || event.key === Key.Backspace) && !!this.input.nativeElement.value) {
                        event.stopPropagation();
                    }
                }
            );
    }

    private subscribeToListNavigation(): Subscription {
        return this.keyDown$
            .pipe(
                // navigate only as long as the dropdown is open
                takeWhile((): boolean => this.open),
                // navigate only with the open and down arrows and only if there is something in the list
                filter((event: KeyboardEvent): boolean =>
                    (
                        event.key === Key.ArrowUp ||
                        event.key === Key.ArrowDown
                    ) &&
                    !!this.filteredElements.length
                )
            ).subscribe((event: KeyboardEvent): void => {
                event.preventDefault();

                const focusIndex: number = event.key === Key.ArrowDown ? 0 : this.filteredElements.length - 1;
                const itemsArr: Array<ElementRef> = this.filteredDOMElements.toArray();
                const focusItem: HTMLLIElement = (itemsArr[focusIndex].nativeElement as HTMLLIElement);
                focusItem.focus();
            });
    }

    private subscribeToInputKeyup(): Subscription {
        return this.keyUp$.pipe(
            tap((event: KeyboardEvent): void => {
                if (event.key === Key.Escape) {
                    this.closeDropdown();
                } else if (event.key === Key.Enter) {
                    this.freeHand.emit(this.input.nativeElement.value);
                    this.filterList(null);
                    this.closeDropdown();
                } else if (event.key !== Key.ArrowLeft && event.key !== Key.ArrowRight) {
                    this.openDropdown();
                }
            }),
            debounceTime(this.delay),
            map((): string => this.filterExpression),
            distinctUntilChanged(
                (previous: string, current: string): boolean => previous === current
            )
        ).subscribe(
            (filterExpression: string): void => {
                setTimeout((): void => {
                    this.filterList(filterExpression);
                });
            }
        );
    }

    private subscribeToInputClick(): Subscription {
        return this.inputClick$
            .subscribe(
                (): void => {
                    if (!this.open) {
                        this.openDropdown();
                        this.input.nativeElement.select();
                    }
                }
            );
    }

    private subscribeToClickOutside(): Subscription {
        return this.host.nativeElement.clickOutside(this.isOpen.bind(this))
            .subscribe(
                (clickedOutside: boolean): void => {
                    if (clickedOutside) { this.closeDropdown(); }
                }
            );
    }

    private proceedInList(event: KeyboardEvent): void {
        event.preventDefault();

        const currentFocused: HTMLElement = event.target as HTMLElement;
        if (event.key === Key.ArrowDown) {
            this.focusNext(currentFocused);
        } else {
            this.focusPrevious(currentFocused);
        }
    }

    private focusNext(currentFocused: HTMLElement): void {
        if (!!currentFocused.nextElementSibling) {
            (currentFocused.nextElementSibling as HTMLElement).focus();
        } else {
            (currentFocused.parentElement.children[0] as HTMLElement).focus();
        }
    }

    private focusPrevious(currentFocused: HTMLElement): void {
        if (!!currentFocused.previousElementSibling) {
            (currentFocused.previousElementSibling as HTMLElement).focus();
        } else {
            const lastIndex: number = currentFocused.parentElement.children.length - 1;
            (currentFocused.parentElement.children[lastIndex] as HTMLElement).focus();
        }
    }
}

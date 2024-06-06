export class Selectable {

    public searchables: Array<string>;

    constructor(
        public display: any,
        public value: any = display,
        ...searchables: Array<string>
    ) {
        if (!!searchables.length) {
            this.searchables = searchables;
        } else {
            this.searchables = [ this.display ];
        }
    }
}

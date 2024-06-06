export default function extensions(): void {
    String.prototype.stripLast = function(): string {
        return this.slice(0, this.length - 1);
    };
    String.prototype.replaceMultipleSlashes = function(): string {
        return this.replace(/\/\/+/g, '/');
    };
    String.prototype.stripProtocol = function(): string {
        return this.replace(/^(?:(http)(s?)\:\/\/)?/, '');
    };
    String.prototype.toCsv = function(): string {
        return this.split('\n').filter(i => i).join(',');
    };
    String.prototype.fromCsv = function(): string {
        return this.split(',').join('\n');
    };
    String.prototype.pascalToHumanReadable = function(): string {
        return this
            // ...aB => ...a B
            .replace(
                /([a-z])([A-Z])/g,
                (...matches: Array<string>): string => matches[0][0] + ' ' + matches[0][1]
            )
            // A(BCDEF)G => A(BCDEF) G
            .replace(
                /([A-Z]+)([A-Z])/g,
                (...matches: Array<string>): string =>
                    matches[0].substr(0, matches[0].length - 1) + ' '
                    + matches[0].substr(matches[0].length - 1)
            );
    };
    Array.prototype.remove = function<T>(item: T): void {
        const index: number = this.indexOf(item);
        if (index > -1) {
            this.splice(index, 1);
        }
    };
    Array.prototype['__defineGetter__']('last', function(): any {
        return this[this.length - 1];
    });
    Array.prototype.unique = function<T>(key: keyof T): Array<T> {
        return (([...new Map(this.map(item => {
            if (item[key] instanceof Date) {
                const hh = item[key] as Date;

                return [hh.valueOf(), item];
            }
            return [item[key], item];
        }
        )).values()] as unknown) as Array<T>);
    };
}

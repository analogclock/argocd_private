export class WindowMock {
    public location: any = {
        _href: '',
        set href(url: string) {
            this._href = url;
        },
        get href(): string {
            return this._href;
        }
    };
}

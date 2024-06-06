//  Application imports
import { ApplicationRoute } from './models/application-route';

export type FadeClass = 'in' | 'out' | 'visible';

export class Utils {
    public static animate(classList: Array<FadeClass> | DOMTokenList, duration: number): void {
        if (classList instanceof DOMTokenList) {
            if (!classList.contains('visible')) {
                classList.add('in');
                classList.add('visible');
                setTimeout((): void => {
                    (classList as DOMTokenList).remove('in');
                }, duration);
            } else if (classList.contains('visible') && !classList.contains('in') && !classList.contains('out')) {
                classList.add('out');
                setTimeout((): void => {
                    (classList as DOMTokenList).remove('out');
                    (classList as DOMTokenList).remove('visible');
                }, duration);
            }
        }
        if (classList instanceof Array) {
            if (classList.length === 0) {
                classList = ['in', 'visible'];
                setTimeout((): void => {
                    classList = ['visible'];
                }, 1000);
            } else if (classList.indexOf('visible') === 0 && classList.length === 1) {
                classList = ['out', 'visible'];
                setTimeout((): void => {
                    classList = [];
                }, 1000);
            }
        }
    }

    public static logoutUrl(): string {
        return `${window.location.origin}/${ApplicationRoute.SPLASH}` ;
    }

    public static sortByOrder(a: { order: number}, b: { order: number }): number {
        if (!a || !a.order || !b || !b.order) { throw Error('Unsortable items in array.'); }
        if (a.order > b.order) { return 1; }
        if (a.order < b.order) { return -1; }
    }
}

//  Application imports
import { Selectable } from './selectable';

describe('Selectable', (): void => {
    it('should construct properly', (): void => {
        expect(new Selectable('display').value).toBe('display');
        expect(new Selectable('display', 'value').searchables).toEqual(['display']);
        expect(new Selectable('display', 'value', 'searchable').searchables).toEqual(['searchable']);
    });
});

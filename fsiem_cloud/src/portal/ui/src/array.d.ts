declare interface Array<T> {
    remove: (item: T) => void;
    last: T;
    unique: (key: keyof T) => Array<T>;
}

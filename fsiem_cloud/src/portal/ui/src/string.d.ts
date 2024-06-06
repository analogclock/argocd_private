declare interface String {
    stripLast: () => string;
    replaceMultipleSlashes: () => string;
    stripProtocol: () => string;
    pascalToHumanReadable: () => string;
    toCsv: () => string;
    fromCsv: () => string;
}

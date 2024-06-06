export class DiskCalculator {
    public static toHuman(bytes: number | string, decimals: number): string {
        let bb: number = 0;
        try {
            bb = Number(bytes);
        } catch {
            bb = 0;
        }

        if (!+bb) { return '0 Bytes'; }

        const k: number = 1000;
        const dm: number = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

        const i: number = Math.floor(Math.log(bb) / Math.log(k));

        return `${parseFloat((bb / Math.pow(k, i)).toFixed(dm))} ${i > 0 ? sizes[i] : sizes[0]}`;
    }
}

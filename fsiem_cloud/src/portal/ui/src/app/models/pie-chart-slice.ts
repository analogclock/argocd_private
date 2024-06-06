export class PieChartSlice {
    constructor(public name: string, public value: number) { }
}

export class LineChartSlice {
    constructor(public name: Date|string, public value: number, public extra?: number) { }
}

export class LineChartSeries {
    public get isEmpty() {
        return !this.series || this.series.length === 0;
    }

    constructor(public name: string|number, public series: Array<LineChartSlice>) { }
}

export class ReferenceLine {
    constructor(public name: string, public value: number) { }
}

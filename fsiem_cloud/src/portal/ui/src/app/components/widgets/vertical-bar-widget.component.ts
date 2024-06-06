import { formatDate } from '@angular/common';
import { Component, Input, OnInit } from '@angular/core';
import { DiskCalculator } from 'app/pipes/disk-calculator';
import { LegendPosition, LineChartModule } from '@swimlane/ngx-charts';
import { LineChartSeries, LineChartSlice } from 'app/models/pie-chart-slice';
import { Selectable } from 'app/dropdown-module/models/selectable';

@Component({
    selector: 'zf-vertical-bar',
    templateUrl: './vertical-bar-widget.component.html',
    styleUrls: ['./vertical-bar-widget.component.scss']
})
export class VerticalBarWidgetComponent implements OnInit {
    public readonly LegendPosition: typeof LegendPosition = LegendPosition;

    @Input()
    public data: Array<LineChartSeries> = [];

    public days: Array<Selectable> = [];

    public day: string;
    public filterData: Array<LineChartSeries> = [];

    public ngOnInit(): void {
        const mo = this.getAllMonths();
        this.filter();
    }

    public filter(): void {
        if (!this.day) {
            this.filterData = this.data;
            return;
        }
        this.filterData = this.data.filter((a) => {
            // force set to start of the month in the format
            const expect = this.fmtDate(a.name, 'yyyy-MM-01T00:00:00Z');
            return expect === this.day;
        });
    }

    public fmtDate(value: any, format: string = 'dd'): string {
        const fmtDate = formatDate(value, format, 'en-US', 'UTC');
        return fmtDate;
    }

    public formatDiskSize(value: number): string {
        return DiskCalculator.toHuman(value, 2);
    }

    public updateDay(event: string): void {
        this.day = event;
        this.filter();
    }

    private getAllMonths(): void {
        const mapper: Map<string, number> = new Map();
        for (const k of this.data) {
            // 2024-02-16T00:00:00+00:00
            const dd = this.fmtDate(k.name, 'yyyy-MM-01T00:00:00Z');
            if (!mapper.get(dd)) {
                mapper.set(dd, 0);
            }

            let old = mapper.get(dd);
            old += k.series[0].value;
            // overwrite existing with new value
            mapper.set(dd, old);
        }

        // format all the months together with the year
        for (const [key, val] of mapper) {
            const ddF = this.fmtDate(key, 'MMMM yyyy');
            const valF = this.formatDiskSize(val);
            this.days.push(new Selectable(`${ddF} (${valF})`, key));
        }

        this.day = this.days.last.value;
    }
}

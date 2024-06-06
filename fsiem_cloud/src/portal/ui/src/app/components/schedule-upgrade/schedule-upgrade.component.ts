import { formatDate } from '@angular/common';
import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { Selectable } from 'app/dropdown-module/models/selectable';
import { UpgradeDatePipe } from 'app/pipes/upgrade-date-pipe';

@Component({
    selector: 'zf-schedule-upgrade',
    templateUrl: './schedule-upgrade.component.html',
    styleUrls: ['./schedule-upgrade.component.scss']
})
export class ScheduledUpgradeComponent implements OnInit {
    @Input()
    public scheduledDate: string;
    @Input()
    public minUpdateDate: Date;
    @Input()
    public maxUpdateDate: Date;

    @Output()
    public scheduledDateChange = new EventEmitter<string>();

    public day: string;
    public hour: string;
    public offset: string;

    public hours: Array<Selectable> = [
        new Selectable('12:00 AM', '00:00'),
        new Selectable('12:30 AM', '00:30'),
        new Selectable('01:00 AM', '01:00'),
        new Selectable('01:30 AM', '01:30'),
        new Selectable('02:00 AM', '02:00'),
        new Selectable('02:30 AM', '02:30'),
        new Selectable('03:00 AM', '03:00'),
        new Selectable('03:30 AM', '03:30'),
        new Selectable('04:00 AM', '04:00'),
        new Selectable('04:30 AM', '04:30'),
        new Selectable('05:00 AM', '05:00'),
        new Selectable('05:30 AM', '05:30'),
        new Selectable('06:00 AM', '06:00'),
        new Selectable('06:30 AM', '06:30'),
        new Selectable('07:00 AM', '07:00'),
        new Selectable('07:30 AM', '07:30'),
        new Selectable('08:00 AM', '08:00'),
        new Selectable('08:30 AM', '08:30'),
        new Selectable('09:00 AM', '09:00'),
        new Selectable('09:30 AM', '09:30'),
        new Selectable('10:00 AM', '10:00'),
        new Selectable('10:30 AM', '10:30'),
        new Selectable('11:00 AM', '11:00'),
        new Selectable('11:30 AM', '11:30'),
        new Selectable('12:00 PM', '12:00'),
        new Selectable('12:30 PM', '12:30'),
        new Selectable('01:00 PM', '13:00'),
        new Selectable('01:30 PM', '13:30'),
        new Selectable('02:00 PM', '14:00'),
        new Selectable('02:30 PM', '14:30'),
        new Selectable('03:00 PM', '15:00'),
        new Selectable('03:30 PM', '15:30'),
        new Selectable('04:00 PM', '16:00'),
        new Selectable('04:30 PM', '16:30'),
        new Selectable('05:00 PM', '17:00'),
        new Selectable('05:30 PM', '17:30'),
        new Selectable('06:00 PM', '18:00'),
        new Selectable('06:30 PM', '18:30'),
        new Selectable('07:00 PM', '19:00'),
        new Selectable('07:30 PM', '19:30'),
        new Selectable('08:00 PM', '20:00'),
        new Selectable('08:30 PM', '20:30'),
        new Selectable('09:00 PM', '21:00'),
        new Selectable('09:30 PM', '21:30'),
        new Selectable('10:00 PM', '22:00'),
        new Selectable('10:30 PM', '22:30'),
        new Selectable('11:00 PM', '23:00'),
        new Selectable('11:30 PM', '23:30')
    ];

    public offsets: Array<Selectable> = [
        new Selectable('UTC-12:00', '-12:00'),
        new Selectable('UTC-11:00', '-11:00'),
        new Selectable('UTC-10:00', '-10:00'),
        new Selectable('UTC-09:30', '-09:30'),
        new Selectable('UTC-09:00', '-09:00'),
        new Selectable('UTC-08:00', '-08:00'),
        new Selectable('UTC-07:00', '-07:00'),
        new Selectable('UTC-06:00', '-06:00'),
        new Selectable('UTC-05:00', '-05:00'),
        new Selectable('UTC-04:00', '-04:00'),
        new Selectable('UTC-03:30', '-03:30'),
        new Selectable('UTC-03:00', '-03:00'),
        new Selectable('UTC-02:00', '-02:00'),
        new Selectable('UTC-01:00', '-01:00'),
        new Selectable('UTC+00:00', '+00:00'),
        new Selectable('UTC+01:00', '+01:00'),
        new Selectable('UTC+02:00', '+02:00'),
        new Selectable('UTC+03:00', '+03:00'),
        new Selectable('UTC+03:30', '+08:30'),
        new Selectable('UTC+04:00', '+04:00'),
        new Selectable('UTC+04:30', '+04:30'),
        new Selectable('UTC+05:00', '+05:00'),
        new Selectable('UTC+05:30', '+05:30'),
        new Selectable('UTC+05:45', '+05:45'),
        new Selectable('UTC+06:00', '+06:00'),
        new Selectable('UTC+06:30', '+06:30'),
        new Selectable('UTC+07:00', '+07:00'),
        new Selectable('UTC+08:00', '+08:00'),
        new Selectable('UTC+08:45', '+08:45'),
        new Selectable('UTC+09:00', '+09:00'),
        new Selectable('UTC+09:30', '+09:30'),
        new Selectable('UTC+10:00', '+10:00'),
        new Selectable('UTC+10:30', '+10:30'),
        new Selectable('UTC+11:00', '+11:00'),
        new Selectable('UTC+12:00', '+12:00'),
        new Selectable('UTC+13:00', '+13:00'),
        new Selectable('UTC+13:45', '+13:45'),
        new Selectable('UTC+14:00', '+14:00')
    ];

    private upgradePipe: UpgradeDatePipe = new UpgradeDatePipe();

    public ngOnInit(): void {
        if (!this.scheduledDate) {
            // default to tomorrow
            const today = new Date();
            this.day = formatDate(today.setDate(today.getDate() + 1), 'yyyy-MM-dd', 'en_US');
            this.hour = '00:00';
            const clientOffset = formatDate(today, 'Z', 'en_US');
            // set the default offset to the current clients offset
            // client offset will be like Z, -0800, +0800
            // if we have 'Z' - we format to +00:00
            // else we standardize to a sensible +01:00 - i.e hour colon minute
            this.offset = clientOffset === 'Z'
                ? '+00:00'
                : `${clientOffset.slice(0, 3)}:${clientOffset.slice(3)}`;

            // we don't have one so make sure everything is on default
            this.generateAndEmit();
        } else {

            this.offset = this.upgradePipe.transform(this.scheduledDate, 'offset');
            this.hour = this.upgradePipe.transform(this.scheduledDate, 'hour');
            this.day = this.upgradePipe.transform(this.scheduledDate, 'day');
        }
    }

    public updateScheduledDate(event: string) {
        if (event) {
            this.day = event;
            this.generateAndEmit();
        }
    }

    public updateTime(event: string): void {
        if (event) {
            this.hour = event;
            this.generateAndEmit();
        }
    }

    public updateTimeZone(event: string): void {
        if (event) {
            this.offset = event;
            this.generateAndEmit();
        }
    }

    private generateAndEmit(): void {
        const formattedLocalDate = `${this.day}T${this.hour}:00${this.offset}`;
        this.emitChange(formattedLocalDate);
    }

    private emitChange(upgrade: string): void {
        this.scheduledDateChange.emit(upgrade);
    }
}

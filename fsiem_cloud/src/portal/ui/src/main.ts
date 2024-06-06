//  Angular imports
import { enableProdMode } from '@angular/core';
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
//  Application imports
import { AppModule } from './app/app.module';
import { environment } from './environments/environment';
import extensions from 'app/extensions';

if (environment.enableProdMode) {
    enableProdMode();
}

extensions();

platformBrowserDynamic().bootstrapModule(AppModule)
    .catch(
        // eslint-disable-next-line no-console
        (err: any): void => console.error(err)
    );

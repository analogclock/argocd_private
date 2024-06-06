//  Angular imports
import { HttpClient, HttpHeaders, HttpResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
//  Application imports
import { environment } from 'environments/environment';
//  Third party imports
import { catchError, first, map, mapTo } from 'rxjs/operators';
import { GenericDeserialize } from 'cerialize';
import { Observable, of } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class BaseProvisioningService {
    public baseUrl: string = environment.provisioningApi;

    constructor(
        private http: HttpClient
    ) { }

    protected apiPost<TRequest, TResponse>(apiPath: string,
        apiBody: TRequest, type: new () => TResponse = null): Observable<any> {
        const url: string = `${this.baseUrl}/${apiPath}`;
        return this.http.post(url, apiBody)
            .pipe(
                first(),
                map(
                    (response: TResponse): TResponse => GenericDeserialize(response, type)
                )
            );
    }

    protected apiPut<TRequest, TResponse>(apiPath: string, apiBody: TRequest, type: new () => TResponse = null): Observable<any> {
        const url: string = `${this.baseUrl}/${apiPath}`;
        return this.http.put(url, apiBody)
            .pipe(
                first(),
                map(
                    (response: TResponse): TResponse => GenericDeserialize(response, type)
                )
            );
    }

    protected apiGet<T>(
        apiPath: string,
        type: new () => T = null,
        observeResponse: boolean = false
    ): Observable<HttpResponse<T | Array<T>> | T | Array<T>> {
        const url: string = `${this.baseUrl}/${apiPath}`;
        // we want to observe the response, so we can't expect a string back (string !== HttpResponse<T>)
        if (observeResponse) {
            return this.http.get(url, { observe: 'response' })
                .pipe(
                    first(),
                    map(
                        (response: HttpResponse<T>): HttpResponse<T | Array<T>> => {
                            if (response.headers.get('Content-Type') === 'application/json') {
                                const responseClone: HttpResponse<T | Array<T>> = new HttpResponse({
                                    body: GenericDeserialize(response.body, type),
                                    headers: response.headers,
                                    status: response.status,
                                    statusText: response.statusText,
                                    url: response.url
                                });
                                return responseClone;
                            }
                            return response;
                        }
                    )
                );
            // we don't care about the response but we need a typed object, so we pass in a truthy constructor as type
        } else if (type !== null) {
            return this.http.get(url)
                .pipe(
                    first(),
                    map(
                        (response: T): T => GenericDeserialize(response, type)
                    )
                );
            // we passed in a null type so we expect a plain string
        } else {
            return this.http.get(url, { responseType: 'text' })
                .pipe(
                    first(),
                    map(
                        (response: string): T => GenericDeserialize(response, type)
                    )
                );
        }
    }

    protected apiDelete(apiPath: string): Observable<boolean> {
        const url: string = `${this.baseUrl}/${apiPath}`;
        return this.http.delete(url)
            .pipe(
                first(),
                mapTo(true),
                catchError(
                    (error: any): Observable<boolean> => {
                        // eslint-disable-next-line no-console
                        console.error(error);
                        return of(false);
                    }
                )
            );
    }

    protected apiDeleteBody<TRequest, TResponse>(apiPath: string, apiBody: TRequest, type: new () => TResponse = null): Observable<any> {
        const url: string = `${this.baseUrl}/${apiPath}`;
        return this.http.delete(url, {
            body: apiBody
        })
            .pipe(
                first(),
                map(
                    (response: TResponse): TResponse => GenericDeserialize(response, type)
                )
            );
    }

    protected apiHead(apiPath: string): Observable<boolean> {
        const url: string = `${this.baseUrl}/${apiPath}`;
        return this.http.head(url)
            .pipe(
                first(),
                mapTo(true),
                catchError((): Observable<boolean> => of(false))
            );
    }
}

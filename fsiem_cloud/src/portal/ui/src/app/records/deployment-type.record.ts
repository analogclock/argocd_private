export enum RDeploymentType {
    ENTERPRISE = 'Enterprise',
    SERVICE_PROVIDER = 'ServiceProvider'
}

// eslint-disable-next-line no-redeclare
export namespace RDeploymentType {
    export const toDisplay: Map<RDeploymentType, string> = new Map<RDeploymentType, string>([
        [RDeploymentType.ENTERPRISE, 'Enterprise'],
        [RDeploymentType.SERVICE_PROVIDER, 'Service Provider']
    ]);

    export const fromStored: Map<string, RDeploymentType> = new Map<string, RDeploymentType>([
        ['va', RDeploymentType.ENTERPRISE],
        ['sp', RDeploymentType.SERVICE_PROVIDER]
    ]);
}

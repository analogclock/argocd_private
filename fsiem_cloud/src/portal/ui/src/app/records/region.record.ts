export enum RRegion {
    CANADA = 'CACentral1',
    NORTH_VIRGINIA = 'USEast1',
    OHIO = 'USEast2',
    OREGON = 'USWest2',
    GERMANY = 'EUCentral1',
    IRELAND = 'EUWest1',
    LONDON = 'EUWest2',
    PARIS = 'EUWest3',
    STOCKHOLM = 'EUNorth1',
    SINGAPORE = 'APSoutheast1',
    SYDNEY = 'APSoutheast2',
    MUMBAI = 'APSouth1'

    // [DH] - The following is commented out until eval COGS
    // have been performed in DEV
    // HONG_KONG = 'APEast1',
    // CAPE_TOWN = 'AFSouth1'

    // [DH] - the following has been commented due to issue with COGS
    // BAHRAIN = 'MESouth1',
}

// eslint-disable-next-line no-redeclare
export namespace RRegion {
    export const toDisplay: Map<RRegion, string> = new Map<RRegion, string>([
        [RRegion.CANADA, 'Canada (Central)'],
        [RRegion.NORTH_VIRGINIA, 'US East (North Virginia)'],
        [RRegion.OHIO, 'US East (Ohio)'],
        [RRegion.OREGON, 'US West (Oregon)'],
        [RRegion.GERMANY, 'Europe (Germany)'],
        [RRegion.IRELAND, 'Europe (Ireland)'],
        [RRegion.LONDON, 'Europe (UK)'],
        [RRegion.PARIS, 'Europe (France)'],
        [RRegion.STOCKHOLM, 'Europe (Sweden)'],
        [RRegion.SYDNEY, 'Asia (Australia)'],
        [RRegion.SINGAPORE, 'Asia (Singapore)'],
        [RRegion.MUMBAI, 'Asia (India)']

        // [DH] - The following is commented out until eval COGS
        // have been performed in DEV
        // [RRegion.HONG_KONG, 'Asia (Hong Kong)'],
        // [RRegion.CAPE_TOWN, 'Africa (South Africa)']

        // [DH] - Has been commented due to issue with COGS
        // [RRegion.BAHRAIN, 'Middle East (Bahrain)']
    ]);
}

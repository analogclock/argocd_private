import { deserialize } from 'cerialize';

export class RExternalStorageDetailModel {
    @deserialize
    public id: string;
    @deserialize
    public serialNumber: string;
    @deserialize
    public organizationId: number;
    @deserialize
    public externalStorageDest: string;
    @deserialize
    public lastStatus: string;
    @deserialize
    public dataTransferred: string;
    @deserialize
    public comments: string;
    // date but strings are much easier to work with
    @deserialize
    public lastUpdate: string;

    public error?: Map<string, string> = new Map();

    public validate(): boolean {
        this.error = new Map();

        if (this.organizationId < -1 || this.organizationId === 0) {
            this.error['organizationId'] = 'Organization ID is not valid, it should be a number greater than 0';
            return false;
        }

        const [bucket, ...rest] = this.externalStorageDest?.split('/') ?? [];

        if (!bucket || bucket.length === 0) {
            // check for empty
            this.error['externalStorageBucket'] = 'Bucket cannot be empty';
            return false;
        }

        if (!bucket.startsWith('fsiemextstr-')) {
            this.error['externalStorageBucket'] = 'Bucket must start with prefix of \'fsiemextstr-\'';
            return false;
        }

        if (!this.isValidS3Bucket(bucket)) {
            return false;
            // this.error['externalStorageBucket'] = 'Bucket name is invalid';
        }

        if (rest && rest.length > 0 && !this.isValidS3Prefix(rest.join('/'))) {
            this.error['externalStorageDirectory'] = 'Bucket prefix is not valid';
            return false;
        }

        return true;
    }

    private isValidS3Bucket(bucketName: string): boolean {

        // https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html
        // Check length between 3 and 63 characters long
        if (!(bucketName.length >= 3 && bucketName.length <= 63)) {
            this.error['externalStorageBucket'] = 'Bucket cannot be less than 3 characters long, or more than 63 characters.';
            return false;
        }

        // Check only lowercase letters, numbers, dots (.), and
        // hyphens (-) allowed
        if (!bucketName.match(/^[a-z0-9.-]+$/)) {
            this.error['externalStorageBucket'] = 'Bucket can only contain lowercase letters, numbers, periods (.), or hyphens (-)';
            return false;
        }

        // Check if the bucket name starts and ends with a letter or number
        if (!(bucketName[0].match(/[a-z0-9]/) || bucketName[-1].match(/[a-z0-9]/))) {
            this.error['externalStorageBucket'] = 'Bucket can only start and end with a letter or number';
            return false;
        }

        // Check consecutive periods
        if (bucketName.match(/\.{2,}/)) {
            this.error['externalStorageBucket'] = 'Bucket cannot contain consecutive periods (..)';
            return false;
        }

        // Check if the bucket name starts or ends with a period
        if (bucketName.startsWith('.') || bucketName.endsWith('.')) {
            this.error['externalStorageBucket'] = 'Bucket cannot start with or end with a period (.)';
            return false;
        }

        // Check if the bucket name starts or ends with a hyphen
        if (bucketName.startsWith('-') || bucketName.endsWith('-')) {
            this.error['externalStorageBucket'] = 'Bucket cannot start with or end with a hyphen (-)';
            return false;
        }

        return true;
    }

    private isValidS3Prefix(prefix: string): boolean {
        // Check allowed characters in the prefix
        if (!prefix.match(/^[a-zA-Z0-9./_-]+$/)) {
            this.error['externalStorageDirectory'] = 'Bucket prefix contains invalid characters. \
            It can only have lower and upper case, numbers, \
            period (.), forward slash (/), underscore (_), and hypen (-) ';
            return false;
        }

        if (prefix.match(/\.{2,}/)) {
            this.error['externalStorageDirectory'] = 'Prefix cannot contain consecutive periods (..)';
            return false;
        }

        return true;
    }
}

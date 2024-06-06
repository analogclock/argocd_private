//  Application imports
import { RAlternateCertificate } from './alternate-certificate.record';
import { RDeploymentType } from './deployment-type.record';
import { RRegion } from './region.record';

import * as forge from 'node-forge';
import IPCIDR from 'ip-cidr';

// const ipCidr = require('ip-cidr');

enum IPVersion {
    IP_4,
    IP_6,
}

export class RActivatedStackInformation {
    public adminPassword: string;
    public confirmAdminPassword: string;
    public ipv4CIDRList: string; // comma-separated list of IPv4 CIDR blocks
    public ipv6CIDRList: string; // comma-separated list of IPv6 CIDR blocks
    public deploymentType: RDeploymentType = RDeploymentType.ENTERPRISE;
    public region: RRegion = RRegion.NORTH_VIRGINIA;
    public shouldUpdateSKU: boolean = false;
    public deploymentEmail: string;
    public additionalContacts: string; // comma-separated list of email addresses
    public alternateDomain: string;
    public certificate: RAlternateCertificate = null;
    public externalStorageDest: string = '';

    public error: Map<string, string> = new Map();

    public validate(isUpdate: boolean = false, updateAlternateDomain: boolean = false): boolean {
        this.error = new Map();
        // validate and add any errors
        if (!isUpdate) {
            // we aren't doing an update here so we should check the admin
            // password
            if (!Boolean(this.adminPassword) || this.adminPassword.length <= 0) {
                this.error['password'] = 'Administrator password is required';
                return false;
            }

            if (!this.matchesComplexity()) {
                return false;
            }

            if (!Boolean(this.confirmAdminPassword) || this.confirmAdminPassword.length <= 0) {
                this.error['confirm-password'] = 'Password confirmation is required';
                return false;
            }

            if (this.adminPassword !== this.confirmAdminPassword) {
                this.error['confirm-password'] = 'Password confirmation doesn\'t match password';
                return false;
            }
        }

        if (!Boolean(this.deploymentType)) {
            this.error['deploymentType'] = `Deployment type '${this.deploymentType}' is required`;
            return false;
        }

        if (!Boolean(this.region)) {
            this.error['region'] = `Region '${this.region}' is required`;
            return false;
        }

        // if both ipv4 and ipv6 are empty it is not a valid state
        if (!Boolean(this.ipv4CIDRList) && !Boolean(this.ipv6CIDRList)) {
            this.error['ipv4'] = 'Both IPV4 and IPV6 CIDR blocks cannot be empty.';
            this.error['ipv6'] = true;
            return false;
        }

        // if we have a value in the ipv4 cidrs, and they are all valid
        if (Boolean(this.ipv4CIDRList) && !this.validCIDRList(this.ipv4CIDRList, IPVersion.IP_4)) {
            return false;
        }

        // if we have a value in the ipv6 cidrs, and they are all valid
        if (Boolean(this.ipv6CIDRList) && !this.validCIDRList(this.ipv6CIDRList, IPVersion.IP_6)) {
            return false;
        }

        if (this.additionalContacts && !this.validEmails(this.additionalContacts)) {
            return false;
        }

        if (updateAlternateDomain && !this.validateDomain()) {
            return false;
        }

        return true;
    }

    private validateDomain(): boolean {
        if (!Boolean(this.alternateDomain)) {
            this.error['alternateDomain'] = 'Alternate domain is required';
            return false;
        }

        if (!this.certificate) {
            this.error['alternatePublicCertificate'] = 'Alternate certificate is required';
            return false;
        }

        if (!Boolean(this.certificate.body)) {
            this.error['alternatePublicCertificate'] = 'Alternate domain public certificate is required';
            return false;
        }

        if (!Boolean(this.certificate.private)) {
            this.error['alternatePrivateCertificate'] = 'Alternate domain private certificate is required';
            return false;
        }

        // we have got some values here we should try and validate them.
        try {
            forge.pki.certificateFromPem(this.certificate.body);
        } catch (e) {
            this.error['alternatePublicCertificate'] = e;
            return false;
        }

        try {
            forge.pki.privateKeyFromPem(this.certificate.private);
        } catch (e) {

            this.error['alternatePrivateCertificate'] = e;
            return false;
        }

        if (Boolean(this.certificate.chain)) {
            try {
                forge.pki.certificateFromPem(this.certificate.chain);
            } catch (e) {
                this.error['alternateChainCertificate'] = e;
                return false;
            }
        }
        return true;
    }

    private matchesComplexity(): boolean {
        const match: RegExpMatchArray =
            // rules are:
            // 1. between 8 - 64
            // 2. at least one upper case char
            // 3. at least one lower case char
            // 4. at least one number
            // 5. at least one special char (using \W + _ regex)
            this.adminPassword.match(/^(?=(.*[a-z].*){1,})(?=(.*[A-Z].*){1,})(?=.*\d.*)(?=.*[\W|_].*)[a-zA-Z0-9\S]{8,64}$/g);
        if (!match || match.length !== 1 || match[0] !== this.adminPassword) {
            this.error['password'] = `Password must be between 8-64 characters,
            with at least 1 uppercase letter,
            1 lowercase letter, 1 number and 1 special character (e.g. $*&%).`;
            return false;
        }

        return true;
    }

    private validEmails(emailListCsv: string): boolean {
        const emails = emailListCsv.split(',');
        for (let i = 0; i < emails.length; i++) {
            const email: string = emails[i];
            // eslint-disable-next-line max-len
            if (!email.match(/^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/)) {
                this.error['additionalContacts'] = `'${email}' is not a valid email`;
                return false;
            }
        }

        return true;
    }

    private validCIDRList(cidrList: string, ipVersion: IPVersion): boolean {
        const cidrs = cidrList.split(',');
        const duplicateCheck = {};
        for (let i = 0; i < cidrs.length; i++) {

            let valid: boolean = true;
            let extra = '';
            const check = cidrs[i];
            if (duplicateCheck[check]) {
                // we have a duplicate
                this.error[ipVersion === IPVersion.IP_4 ? 'ipv4' : 'ipv6'] = `CIDR (${check}) already exist remove duplicate entry.`;
                return false;
            } else {
                // for next time
                duplicateCheck[check] = true;
            }

            // the checks below break when using these so we
            // will short circuit them.
            if(check === '0.0.0.0/0' || check === '::/0') {
                continue;
            }

            valid = IPCIDR.isValidCIDR(check);
            if (valid) {
                const ip = new IPCIDR(check);
                const split = check.split('/');
                const start = ip.start();

                // take the left (from: 10.1.1.1/29) and check if
                // it it the same as the start address
                if (split[0] !== start) {
                    valid = false;
                    extra = ` - block must be in continuous block starting from ${start}/${split[1]}`;
                }
            }

            if (valid === false || !valid) {
                // set error
                this.error[ipVersion === IPVersion.IP_4 ? 'ipv4' : 'ipv6'] = `'${check}' is not a valid CIDR block${extra}`;
                return false;
            }

        }

        return true;
    }
}

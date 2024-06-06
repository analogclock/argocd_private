# FortiSIEMPortal

This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 7.1.4, and updated to later version.

## Ubuntu 22.04 setup

Install nodjs using the version from the Dockerfile and angular by running the following:

```bash
cd ~
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
NODE_MAJOR=20
echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | sudo tee /etc/apt/sources.list.d/nodesource.list
sudo apt-get update
sudo apt-get install nodejs -y
sudo npm install -g @angular/cli
```

Verify the installed versions:

```bash
node -v
npm -v
ng version
```

To run locally for the first time:

```bash
cd src/portal/ui
ng build --configuration=local
npm run playground
```

In your browser use https://localhost:4201 to connect to the angular dev server that has been created. Port 4201 is specified in one of the files and sent to cloud team as an allowable port for login, no other port can be used.

`npm run playground` will connect you to the api for fortisiem-playground.forticloud.com. Run `npm run dev` if you want to connect to fortisiem-dev.forticloud.com.

## Development

Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.

Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory. Use the `--prod` flag for a prod build.

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io). Tests require a browser, such as Chrome. Run `ng e2e` to execute the end-to-end tests via [Protractor](http://www.protractortest.org/).

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI README](https://github.com/angular/angular-cli/blob/master/README.md).

Tips to update runtime and build dependencies:
- Do NOT update `package-lock.json` file manually, it is manitained by automated tools and is generated from `package.json`
- To update `package.json` file, install the required `node` version (for example via using NVM), check `build.Dockerfile` to figure out which version of `node` is required - it will be defined in the `FROM` instruction
- Install `angular-cli`, check `package.json` for the needed version
- Run update commands:

  ```bash
  npm install
  npm update
  npm audit fix

  ng update

  # If stuff doesn't work, do it in steps
  # You could try --force with the commands
  # Sometimes, you may need to manually edit the package.json file.
  # Be very careful with manual edits.
  # Always test your application after the upgrade.
  ```

## Deployment

Build script runs build in a container and copies artifacts to the `artifacts` folder at the root of this project.

## Requirements
You must obtain an SSL certificate that is valid for the domain you want to use to front the portal before attempting the deployment or else it will fail. You then need to provide the ARN of this certificate as a parameter for the CloudFormation template. This certificate must be obtained using Amazon Certificate Manager in the us-east-1 (North Virginia) region as this is a requirment for CloudFront.

## Security
 - The deployment allows the S3 bucket to be accessible only through CloudFront. This prevents enumeration of objects within the bucket and means the bucket does not have to be public.
 - The CloudFront distribution requires a client to connect with at least TLS 1.2. This is compatible with all major browsers.

 ## Portal Updates
 For the initial deployment and any subsequent updates to the portal, upload the entirety of the `/dist/fortisiem-portal` that is created with `ng build` directory to the S3 bucket this provisions.

 When you update files, it may take a while for these changes to be reflected because CloudFront is a CDN and caches the content. You may invalidate the cache and force new content to be retrieved by following instructions [here](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Invalidation.html).

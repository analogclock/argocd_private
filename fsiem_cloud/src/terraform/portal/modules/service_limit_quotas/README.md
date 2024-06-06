This module manages the service limit quotas in a region. If existing quotas in a region do not match what is set in the code then it will automatically raise a service limit request to AWS for us.

Please do not add more than one new quota at a time (keep this in mind for prod as well as dev/playground). There is a limit to the number of quota requests that can be open at once. If you add too many then the deploy will fail as it will fail with `QuotaExceededException`.

If you receive error: `Error: error getting Default Service Quota for (vpc/L-0263D0A3): NoSuchResourceException:`. It may be because you out in the wrong service_code for the quota. The error may persist after you remove/change the resource or change to a different branch. This is an error in the state file. Download it from S3, identify the left over resource in the file, then reupload it to the same s3 location.

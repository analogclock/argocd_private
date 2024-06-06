# Hooks

These scripts update state of a particular customer deployment.

## Lifecycle

The following commands demonstrate expected lifecycle that is implemented via
shell hooks in this folder.

```shell
# setup
TBL="fsiem_activation_table_playground"
SN="fsiem-omandryc-0"
CMD="INSERT INTO $TBL VALUE {'serialNumber':'$SN'}"
aws dynamodb execute-statement --region us-east-1 --statement "$CMD"

# actual commands used by the hooks scripts
CMD="UPDATE $TBL SET status='CreateInProgress' WHERE serialNumber='$SN'"
aws dynamodb execute-statement --region us-east-1 --statement "$CMD"

CMD="UPDATE $TBL SET status='LicenseInProgress' SET url='https://super.com'
     SET workersUrl='https://worker.com' WHERE serialNumber='$SN'"
aws dynamodb execute-statement --region us-east-1 --statement "$CMD"

CMD="UPDATE $TBL SET status='CreateFailed' WHERE serialNumber='$SN'"
aws dynamodb execute-statement --region us-east-1 --statement "$CMD"

CMD="UPDATE $TBL SET status='DeleteInProgress' WHERE serialNumber='$SN'"
aws dynamodb execute-statement --region us-east-1 --statement "$CMD"

CMD="UPDATE $TBL SET status='DeleteFailed' WHERE serialNumber='$SN'"
aws dynamodb execute-statement --region us-east-1 --statement "$CMD"

CMD="DELETE FROM $TBL WHERE serialNumber='$SN'"
aws dynamodb execute-statement --region us-east-1 --statement "$CMD"
```

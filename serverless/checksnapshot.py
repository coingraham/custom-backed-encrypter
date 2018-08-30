import boto3
from botocore import exceptions as botofail


def run(event, context):

    region = event["region"]

    if "encrypted_snap_id" in event:
        snapshot_id = event['encrypted_snap_id']
    else:
        snapshot_id = event["volume_details"]["Snapshot_Id"]

    print snapshot_id

    try:
        session = boto3.session.Session(region_name=region)
        ec2_client = session.client("ec2")
        waiter_snapshot_complete = ec2_client.get_waiter("snapshot_completed")

        # Set the max_attempts for this waiter (default 40)
        waiter_snapshot_complete.config.max_attempts = 2

        try:
            waiter_snapshot_complete.wait(
                SnapshotIds=[
                    snapshot_id,
                ]
            )

            return "Complete"

        except botofail.WaiterError:

            return "Running"

    except Exception as lambda_e:

        print "Step Function Encrypter failed with the following information:\n\n" \
              "Exception arguments:\n{}\n\n" \
              "Exception message:\n{}\n\n".format(lambda_e.args, lambda_e.message)

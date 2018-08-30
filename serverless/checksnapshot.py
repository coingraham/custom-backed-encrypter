import boto3
from botocore import exceptions as botofail


def run(event, context):

    region = "us-east-1"

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


# Main for local testing
if __name__ == '__main__':

    local_region = "us-east-1"
    profile = "firstwatch"
    instance_id = "i-067189546fe247695"

    volume_details = {
        "DeviceName": "/dev/xvda",
        "Volume_Tags": "",
        "VolumeId": "vol-0c505e0b42159b9b8",
        "Volume_Type": "gp2",
        "Volume_AZ": "us-east-1d",
        "DeleteOnTermination": "true",
        "Snapshot_Id": "snap-0c72fc0165da96af4"
    }

    snapshot_id = "snap-042c90e0bf510cea0"

    try:
        session = boto3.session.Session(region_name=local_region, profile_name=profile)
        ec2_client = session.client("ec2")
        waiter_snapshot_complete = ec2_client.get_waiter("snapshot_completed")

        # Set the max_attempts for this waiter (default 40)
        waiter_snapshot_complete.config.max_attempts = 5

        try:
            waiter_snapshot_complete.wait(
                SnapshotIds=[
                    snapshot_id,
                ]
            )

            print "Complete"

        except botofail.WaiterError:

            print "Running"

    except Exception as local_e:

        print "Step Function Encrypter failed with the following information:\n\n" \
              "Exception arguments:\n{}\n\n" \
              "Exception message:\n{}\n\n".format(local_e.args, local_e.message)



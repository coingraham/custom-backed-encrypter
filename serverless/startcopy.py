import boto3


def run(event, context):

    region = "us-east-1"

    if "instance_id" in event:
        event_instance_id = event['instance_id']
    else:
        return "Missing Instance ID"

    snapshot_id = event["volume_details"]["Snapshot_Id"]

    print snapshot_id

    try:
        session = boto3.session.Session(region_name=region)
        ec2_resource = session.resource("ec2")
        snapshot_obj = ec2_resource.Snapshot(snapshot_id)
        snapshot_encrypted = snapshot_obj.copy(
            SourceRegion=region,
            Description="Encrypted copy of snapshot ({}) for {}".format(snapshot_id, event_instance_id),
            Encrypted=True,
        )

        print snapshot_encrypted

        return snapshot_encrypted["SnapshotId"]

    except Exception as lambda_e:

        print "Step Function Encrypter failed with the following information:\n\n" \
              "Exception arguments:\n{}\n\n" \
              "Exception message:\n{}\n\n".format(lambda_e.args, lambda_e.message)


# Main for local testing
if __name__ == '__main__':

    region = "us-east-1"
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

    try:
        session = boto3.session.Session(region_name=region, profile_name=profile)
        ec2_resource = session.resource("ec2")
        snapshot_obj = ec2_resource.Snapshot(volume_details["Snapshot_Id"])
        snapshot_encrypted = snapshot_obj.copy(
            SourceRegion=region,
            Description="Encrypted copy of snapshot ({}) for {}".format(volume_details["Snapshot_Id"], instance_id),
            Encrypted=True,
        )

        print snapshot_encrypted["SnapshotId"]

    except Exception as local_e:

        print "Step Function Encrypter failed with the following information:\n\n" \
              "Exception arguments:\n{}\n\n" \
              "Exception message:\n{}\n\n".format(local_e.args, local_e.message)



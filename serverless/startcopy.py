import boto3


def run(event, context):

    region = event["region"]

    event_instance_id = event['instance_id']

    event_snapshot_id = event["volume_details"]["Snapshot_Id"]

    try:
        session = boto3.session.Session(region_name=region)
        ec2_resource = session.resource("ec2")
        snapshot_obj = ec2_resource.Snapshot(event_snapshot_id)
        snapshot_encrypted = snapshot_obj.copy(
            SourceRegion=region,
            Description="Encrypted copy of snapshot ({}) for {}".format(event_snapshot_id, event_instance_id),
            Encrypted=True,
        )

        return snapshot_encrypted["SnapshotId"]

    except Exception as lambda_e:

        print "Step Function Encrypter failed with the following information:\n\n" \
              "Exception arguments:\n{}\n\n" \
              "Exception message:\n{}\n\n".format(lambda_e.args, lambda_e.message)

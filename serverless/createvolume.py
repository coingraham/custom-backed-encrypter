import boto3


def run(event, context):

    region = "us-east-1"

    encrypted_snap_id = event['encrypted_snap_id']
    availability_zone = event["volume_details"]["Volume_AZ"]
    volume_type = event["volume_details"]["Volume_Type"]

    print encrypted_snap_id

    try:
        session = boto3.session.Session(region_name=region)
        ec2_resource = session.resource("ec2")

        volume_encrypted = ec2_resource.create_volume(
            SnapshotId=encrypted_snap_id,
            AvailabilityZone=availability_zone,
            VolumeType=volume_type,
        )

        return volume_encrypted.id

    except Exception as lambda_e:

        print "Step Function Encrypter failed with the following information:\n\n" \
              "Exception arguments:\n{}\n\n" \
              "Exception message:\n{}\n\n".format(lambda_e.args, lambda_e.message)

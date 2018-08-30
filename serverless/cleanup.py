import boto3
from botocore import exceptions as boto_fail


def run(event, context):

    region = event["region"]
    instance_id = event["instance_id"]
    device_name = event["volume_details"]["DeviceName"]
    encrypted_volume_id = event["encrypted_volume_id"]
    original_volume_id = event["volume_details"]["VolumeId"]
    volume_tags = event["volume_details"]["Volume_Tags"]
    delete_on_termination = event["volume_details"]["DeleteOnTermination"]
    original_snapshot_id = event["volume_details"]["Snapshot_Id"]
    encrypted_snapshot_id = event['encrypted_snap_id']

    try:

        session = boto3.session.Session(region_name=region)
        ec2_resource = session.resource("ec2")
        ec2_client = session.client("ec2")
        waiter_volume_available = ec2_client.get_waiter("volume_available")

        # Set the max_attempts for this waiter (default 40)
        waiter_volume_available.config.max_attempts = 2

        # Get the various objects
        volume_encrypted = ec2_resource.Volume(encrypted_volume_id)
        instance = ec2_resource.Instance(instance_id)

        # Update the tags to match the old tags if they exist
        if volume_tags:
            volume_encrypted.create_tags(Tags=volume_tags)

        # Get the instance object

        # Switch the original volume for the new volume.
        instance.detach_volume(
            VolumeId=original_volume_id,
            Device=device_name,
        )

        # Wait for the old volume to be detached before attaching the new volume.
        try:
            waiter_volume_available.wait(
                VolumeIds=[
                    original_volume_id,
                ],
            )

        except boto_fail.WaiterError as e:
            return "Error: {}\nVolume with ID: {} did not detach from {} in time.  Clean up: \nSnap {}, {}\nVolume {}".\
                format(e,
                       original_volume_id,
                       instance_id,
                       original_snapshot_id,
                       encrypted_snapshot_id,
                       encrypted_volume_id)

        instance.attach_volume(
            VolumeId=encrypted_volume_id,
            Device=device_name
        )

        # Modify instance volume attributes to match the original.
        instance.modify_attribute(
            BlockDeviceMappings=[
                {
                    "DeviceName": device_name,
                    "Ebs": {
                        "DeleteOnTermination": delete_on_termination,
                    },
                },
            ],
        )

        # Delete snapshots and original volume
        ec2_resource.Snapshot(original_snapshot_id).delete()
        ec2_resource.Snapshot(encrypted_snapshot_id).delete()
        ec2_resource.Volume(original_volume_id).delete()

        # Start the instance
        instance.start()

        return "Complete"

    except Exception as lambda_e:

        print "Step Function Encrypter failed with the following information:\n\n" \
              "Exception arguments:\n{}\n\n" \
              "Exception message:\n{}\n\n".format(lambda_e.args, lambda_e.message)

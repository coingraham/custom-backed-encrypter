import boto3
from botocore import exceptions as botofail


class SnapshotStarter:
    
    def __init__(self, instance_id, region):
        self.instance_id = instance_id
        self.region = region
        self.instance = None
        self.instance_volume_mappings = []
        self.session = boto3.session.Session(region_name=self.region)
        self.ec2_client = self.session.client("ec2")
        self.ec2_resource = self.session.resource("ec2")
        self.waiter_instance_stopped = self.ec2_client.get_waiter("instance_stopped")

    def start(self):

        try:

            # Get instance resource from instance id
            self.instance = self.ec2_resource.Instance(self.instance_id)

            # Save instance volume mappings and tags to persist to new volume
            for block_device_mapping in self.instance.block_device_mappings:
                if block_device_mapping["DeviceName"] == self.instance.root_device_name:
                    device_id = block_device_mapping["Ebs"]["VolumeId"]
                    device_name = block_device_mapping["DeviceName"]
                    delete_on_termination = block_device_mapping["Ebs"]["DeleteOnTermination"]
                    volume = self.ec2_resource.Volume(device_id)
                    self.instance_volume_mappings.append({
                        "VolumeId": device_id,
                        "Volume": volume,
                        "Volume_Tags": volume.tags,
                        "Volume_Type": volume.volume_type,
                        "DeleteOnTermination": delete_on_termination,
                        "DeviceName": device_name,
                        "Volume_AZ": self.instance.placement["AvailabilityZone"]
                    })

            # If there are any volumes to action against, stop the instance.
            self.stop_instance()

            for volume in self.instance_volume_mappings:
                snap_id = self.process_volume(volume["Volume"])
                volume["Snapshot_Id"] = snap_id
                del volume["Volume"]

            return self.instance_volume_mappings[0]

        except Exception as lambda_e:

            print "Step Function Starter failed with the following information:\n\n" \
                  "Exception arguments:\n{}\n\n" \
                  "Exception message:\n{}\n\n".format(lambda_e.args, lambda_e.message)

    def process_volume(self, volume):

        snapshot = self.ec2_resource.create_snapshot(
            VolumeId=volume.id,
            Description="Snapshot of volume ({}) for {}".format(volume.id, self.instance_id),
        )

        return snapshot.id

    def stop_instance(self):
        # Exit if instance is pending, shutting-down, or terminated
        instance_exit_states = [0, 32, 48]
        if self.instance.state["Code"] in instance_exit_states:
            raise Exception("ERROR: Instance is {} please make sure this instance ({}) is active.".format(
                self.instance.state["Name"],
                self.instance_id
            ))

        # Validate successful shutdown if it is running or stopping
        if self.instance.state["Code"] is 16:
            self.instance.stop()

        # Set the max_attempts for this waiter (default 40)
        self.waiter_instance_stopped.config.max_attempts = 40

        try:
            self.waiter_instance_stopped.wait(
                InstanceIds=[
                    self.instance.id,
                ]
            )
        except botofail.WaiterError as e:
            raise Exception("ERROR: {} on {}".format(e, self.instance_id))

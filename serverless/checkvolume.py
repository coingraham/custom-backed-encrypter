import boto3
from botocore import exceptions as botofail


def run(event, context):

    region = "us-east-1"

    encrypted_volume_id = event['encrypted_volume_id']

    try:
        session = boto3.session.Session(region_name=region)
        ec2_client = session.client("ec2")
        waiter_volume_available = ec2_client.get_waiter("volume_available")

        # Set the max_attempts for this waiter (default 40)
        waiter_volume_available.config.max_attempts = 2

        try:
            waiter_volume_available.wait(
                VolumeIds=[
                    encrypted_volume_id,
                ],
            )

            return "Complete"

        except botofail.WaiterError:

            return "Running"

    except Exception as lambda_e:

        print "Step Function Encrypter failed with the following information:\n\n" \
              "Exception arguments:\n{}\n\n" \
              "Exception message:\n{}\n\n".format(lambda_e.args, lambda_e.message)

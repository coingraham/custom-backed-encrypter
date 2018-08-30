from snapshotstarter import SnapshotStarter


def run(event, context):

    if event['instance_id']:
        event_instance_id = event['instance_id']
    else:
        return "Missing Instance ID"

    # if event['aws_encryption_key_arn']:
    #     event_aws_encryption_key_arn = event['aws_encryption_key_arn']
    # else:
    #     return "Missing Instance ID"

    try:
        lambda_snapshot_starter = SnapshotStarter(event_instance_id)

        return lambda_snapshot_starter.start()

    except Exception as lambda_e:

        print "Step Function Encrypter failed with the following information:\n\n" \
              "Exception arguments:\n{}\n\n" \
              "Exception message:\n{}\n\n".format(lambda_e.args, lambda_e.message)


# Main for local testing
if __name__ == '__main__':

    local_profile = "firstwatch"
    local_region = "us-east-1"
    local_instance_id = "i-067189546fe247695"
    local_aws_encryption_key_arn = ""

    try:
        snapshot_starter = SnapshotStarter(local_instance_id, local_profile)

        print snapshot_starter.start()

    except Exception as local_e:

        print "Step Function Encrypter failed with the following information:\n\n" \
              "Exception arguments:\n{}\n\n" \
              "Exception message:\n{}\n\n".format(local_e.args, local_e.message)



from snapshotstarter import SnapshotStarter


def run(event, context):

    region = event["region"]
    event_instance_id = event['instance_id']

    try:
        lambda_snapshot_starter = SnapshotStarter(event_instance_id, region)

        return lambda_snapshot_starter.start()

    except Exception as lambda_e:

        print "Step Function Encrypter failed with the following information:\n\n" \
              "Exception arguments:\n{}\n\n" \
              "Exception message:\n{}\n\n".format(lambda_e.args, lambda_e.message)

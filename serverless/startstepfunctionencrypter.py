from stepfunctionstarter import StepFunctionStarter
import requests
import json


def run(event, context):

    print event

    event_instance_id = event["ResourceProperties"]["instance_id"]
    event_step_function_arn = event["ResourceProperties"]["step_function_arn"]
    requesttype = event["RequestType"]

    responseStatus = "SUCCESS"
    responseData = {}
    if requesttype == "Delete":
        return sendResponse(event, context, responseStatus, responseData)

    try:
        step_function_encrypter = StepFunctionStarter(event_instance_id, event_step_function_arn)

        step_function_encrypter.start()

        responseStatus = "SUCCESS"
        return sendResponse(event, context, responseStatus, responseData)

    except Exception as lambda_e:

        print "Step Function Encrypter failed with the following information:\n\n" \
              "Exception arguments:\n{}\n\n" \
              "Exception message:\n{}\n\n".format(lambda_e.args, lambda_e.message)

        responseStatus = "FAILURE"
        return sendResponse(event, context, responseStatus, responseData)


def sendResponse(event, context, responseStatus, responseData):
    responseBody = {'Status': responseStatus,
                    'Reason': 'See the details in CloudWatch Log Stream: ' + context.log_stream_name,
                    'PhysicalResourceId': context.log_stream_name,
                    'StackId': event['StackId'],
                    'RequestId': event['RequestId'],
                    'LogicalResourceId': event['LogicalResourceId'],
                    'Data': responseData}
    print 'RESPONSE BODY:n' + json.dumps(responseBody)
    try:
        req = requests.put(event['ResponseURL'], data=json.dumps(responseBody))
        if req.status_code != 200:
            print req.text
            raise Exception('Recieved non 200 response while sending response to CFN.')
        return
    except requests.exceptions.RequestException as e:
        print e
        raise

# Main for local testing
if __name__ == '__main__':

    local_instance_id = "i-06d4151908600b5d4"
    local_step_function_arn = "arn:aws:states:us-east-1:955241386426:stateMachine:test2"
    local_profile = "firstwatch"

    try:
        local_step_function_encrypter = StepFunctionStarter(local_instance_id, local_step_function_arn, local_profile)

        local_step_function_encrypter.start()

    except Exception as local_e:

        print "Step Function Encrypter failed with the following information:\n\n" \
              "Exception arguments:\n{}\n\n" \
              "Exception message:\n{}\n\n".format(local_e.args, local_e.message)



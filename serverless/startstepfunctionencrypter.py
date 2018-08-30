from stepfunctionstarter import StepFunctionStarter
import requests
import json


def run(event, context):

    print event

    event_instance_id = event["ResourceProperties"]["instance_id"]
    event_step_function_arn = event["ResourceProperties"]["step_function_arn"]
    request_type = event["RequestType"]

    response_status = "SUCCESS"
    response_data = {}
    if request_type == "Delete":
        return send_response(event, context, response_status, response_data)

    try:
        step_function_encrypter = StepFunctionStarter(event_instance_id, event_step_function_arn)

        step_function_encrypter.start()

        response_status = "SUCCESS"
        return send_response(event, context, response_status, response_data)

    except Exception as lambda_e:

        print "Step Function Encrypter failed with the following information:\n\n" \
              "Exception arguments:\n{}\n\n" \
              "Exception message:\n{}\n\n".format(lambda_e.args, lambda_e.message)

        response_status = "FAILURE"
        return send_response(event, context, response_status, response_data)


def send_response(event, context, response_status, response_data):
    response_body = {
        "Status": response_status, 
        "Reason": "See the details in CloudWatch Log Stream: " + context.log_stream_name,
        "PhysicalResourceId": context.log_stream_name,
        "StackId": event["StackId"],
        "RequestId": event["RequestId"],
        "LogicalResourceId": event["LogicalResourceId"],
        "Data": response_data
    }
    print "RESPONSE BODY: \n" + json.dumps(response_body)

    try:
        req = requests.put(event["ResponseURL"], data=json.dumps(response_body))
        if req.status_code != 200:
            print req.text
            raise Exception("Received non 200 response while sending response to CFN.")
        return
    except requests.exceptions.RequestException as request_e:
        print "Step Function Encrypter failed with the following information:\n\n" \
              "Exception arguments:\n{}\n\n" \
              "Exception message:\n{}\n\n".format(request_e.args, request_e.message)
        raise

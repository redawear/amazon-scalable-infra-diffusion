import json

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import os
import boto3
import requests
import random

lambda_client = boto3.client('lambda')
# Create SQS client
sqs = boto3.client('sqs')
QUEUE_URL = os.environ.get("SQS_QUEUE_URL")
APPLICATION_ID = os.environ.get("APPLICATION_ID")

PUBLIC_KEY = os.environ.get("PUBLIC_KEY") # found on Discord Application -> General Information page
RESPONSE_TYPES =  { 
                    "PONG": 1, 
                    "CHANNEL_MESSAGE_WITH_SOURCE": 4,
                    "DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE": 5,
                    "DEFERRED_UPDATE_MESSAGE": 6,
                    "UPDATE_MESSAGE": 7,
                    "APPLICATION_COMMAND_AUTOCOMPLETE_RESULT": 8,
                    "MODAL": 9
                  }

def sendSQSMessage(customer_data, user_id, model_id):
    # Send message to SQS queue
    MyMessageAttributes = {}
    for customer_request in customer_data:
        MyMessageAttributes[customer_request] = {
                'DataType': 'String',
                'StringValue': str(customer_data[customer_request])
            }
    if "negative_prompt" in MyMessageAttributes:
        MyMessageAttributes['prompt']['StringValue'] = f"{MyMessageAttributes['prompt']['StringValue']}###{MyMessageAttributes['negative_prompt']['StringValue']}"
    MyMessageAttributes.update({
        'userId': {
            'DataType': 'Number',
            'StringValue': str(user_id)
        },
        'username': {
            'DataType': 'String',
            'StringValue': str(username)
        },
        'applicationId': {
            'DataType': 'String',
            'StringValue': str(application_id)
        },
    })
    # print(MyMessageAttributes)
    response = sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageAttributes=MyMessageAttributes,
        MessageBody=json.dumps(MyMessageAttributes),
        # Each request gets processed randomly
        # MessageGroupId=f'{user_id}{random.randint(0,99999)}'
        # Each request is processed one at a time for a user. Multiple user requests are processed at once if > 1 machine.
        MessageGroupId=user_id
    )
    # print(response['MessageId'])
    return MyMessageAttributes
    
    message = auth_ts.encode() + raw_body.encode()
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    verify_key.verify(message, bytes.fromhex(auth_sig)) # raises an error if unequal

def ping_pong(body):
    if body.get("type") == 1:
        return True
    return False


def validateRequest(r):
    if not r.ok:
        print("Failure")
        raise Exception(r.text)
    else:
        print("Success")
    return

def messageResponse(customer_data):
    message_response = f"\nPrompt: {customer_data['prompt']}"
    if 'negative_prompt' in customer_data:
        message_response += f"\nNegative Prompt: {customer_data['negative_prompt']}"
    if 'seed' in customer_data:
        message_response += f"\nSeed: {customer_data['seed']}"
    if 'steps' in customer_data:
        message_response += f"\nSteps: {customer_data['steps']}"
    if 'sampler' in customer_data:
        message_response += f"\nSampler: {customer_data['sampler']}"
    return message_response

def lambda_handler(event, context):
    print(f"{event}") # debug print
        
    # check if message is a ping
    request_data = json.loads(event['body'])
    text_prompt = request_data.get("text_prompt")
    user_id = request_data.get("user_id")
    model_id = request_data.get("model_id")
    
    # Collect customer data
    info = json.loads(event.get("body"))
    # print(info)
    customer_data = {
    'prompt': text_prompt,
    'negative_prompt': 'your_fixed_negative_prompt',
    'seed': 'your_fixed_seed',
    'steps': 'your_fixed_steps',
    'sampler': 'your_fixed_sampler',
    'user_id': user_id,
    'model_id': model_id
    }

    
    # Trigger async lambda for picture generation
    # print(f"Payload = {info}")
    # lambda_client.invoke(FunctionName='discord_stable_diffusion_backend',
                        #  InvocationType='Event',
                        #  Payload=json.dumps(info))
    
    # Send work to SQS Queue
    sendSQSMessage(customer_data, user_id, model_id)
    message_response = messageResponse(customer_data)
    # Respond to user
    print("Going to return some data!")
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"Submitted to Sparkle: {message_response}"
        })
    }

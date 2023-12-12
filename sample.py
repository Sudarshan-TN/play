import json
import os
import uuid

import boto3
import construct as c
import websocket

ecs_client = boto3.client('ecs', region_name='us-east-1')
ssm = boto3.client("ssm", region_name='us-east-1')
# Define the cluster and task name
cluster_name = 'engineering-tools'

task_name = os.getenv('TASK_NAME')
# Get the task details to retrieve the container's ID
response = ecs_client.describe_tasks(cluster=cluster_name, tasks=[task_name])

response_execute_command = ecs_client.execute_command(
    cluster=os.getenv('CLUSTER'),
    container='hub',
    command="tail -n 1 /etc/hosts",
    interactive=True,
    task=os.getenv('TASK')
)
# Get the output of the command executed inside the container
session = response_execute_command['session']

connection = websocket.create_connection(session['streamUrl'])

try:
    init_payload = {
        "MessageSchemaVersion": "1.0",
        "RequestId": str(uuid.uuid4()),
        "TokenValue": session['tokenValue']
    }
    connection.send(json.dumps(init_payload))

    AgentMessageHeader = c.Struct(
        'HeaderLength' / c.Int32ub,
        'MessageType' / c.PaddedString(32, 'ascii'),
    )

    AgentMessagePayload = c.Struct(
        'PayloadLength' / c.Int32ub,
        'Payload' / c.PaddedString(c.this.PayloadLength, 'ascii')
    )

    while True:
        response = connection.recv()

        message = AgentMessageHeader.parse(response)

        if 'channel_closed' in message.MessageType:
            raise Exception('Channel closed before command output was received')
        if 'output_stream_data' in message.MessageType:
            break

finally:
    connection.close()
payload_message = AgentMessagePayload.parse(response[message.HeaderLength:])
print(payload_message.Payload.split()[0])

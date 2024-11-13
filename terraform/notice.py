import os
import json
from http.client import HTTPResponse
from urllib.request import Request
from urllib.request import urlopen

import boto3


SECRET_NAME = os.environ.get("SLACK_WEBHOOK_SECRET_NAME")
SECRETS_TO_EXPECT = ["SLACK_WEBHOOK_URL"]


class SecretNotFound(Exception):
    pass


def load_secret(name):

    client = boto3.client("secretsmanager")
    secrets = json.loads(client.get_secret_value(SecretId=name)["SecretString"])
    for key, value in secrets.items():
        os.environ[key] = str(value)


def handler(event, _):

    load_secret(SECRET_NAME)
    for secret_name in SECRETS_TO_EXPECT:
        if not os.environ.get(secret_name):
            raise SecretNotFound(
                f"Could not find {secret_name} in environment."
            )

    message = json.loads(event["Records"][0]["Sns"]["Message"])
    container = message["detail"]["containers"][0]
    if container["exitCode"] == 0:
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "ok"})
        }
    else:
        slack_message = {
            "text": message["detail"]["stoppedReason"],
            "attachments": [{
                "color": "danger",
                "fields": [{
                    "title": "ECS Task",
                    "value": container["name"],
                    "short": True
                }, {
                    "title": "Timestamp",
                    "value": message["time"],
                    "short": True
                }, {
                    "title": "Exit Code",
                    "value": container["exitCode"],
                    "short": True
                }, {
                    "title": "Region",
                    "value": message["region"],
                    "short": True
                }, {
                    "title": "AWS Account",
                    "value": message["account"],
                    "short": True
                }]
            }]
        }

        response: HTTPResponse = urlopen(
            Request(
                os.environ["SLACK_WEBHOOK_URL"],
                data=json.dumps(slack_message).encode("utf8"),
                headers={"Content-Type": "application/json"}
            )
        )

        return {
            "statusCode": response.status,
            "isBase64Encoded": False,
            "body": json.dumps(response.read().decode("utf8"))
        }

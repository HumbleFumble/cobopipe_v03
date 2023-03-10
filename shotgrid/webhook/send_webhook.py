import requests
import json
import os
import hmac
import hashlib

token = '97806dc14d1045b4adabbbb7fd90f193'

def send_webhook():
    url = "http://192.168.0.89:21225/remote"
    # path = os.path.abspath(os.path.join(__file__, '..', 'data.json'))
    # data = get_json(path)
    headers = {'content-type': 'application/json; charset=utf-8'}
    data = {"Test": "This is a test"}
    body = json.dumps(data)
    headers['signature'] = generate_signature(body)
    requests.post(url, json=data, headers=headers)


def get_json(file_path):
    if not os.path.exists(file_path):
        print("Not a valid directory.")
        return None

    if not os.path.isfile(file_path):
        print("Directory is not a file.")
        return None

    with open(file_path, "r") as file:
        data = json.load(file)
    if data:
        return data


def generate_signature(body):
    # DO NOT TOUCH - PLEASE
    secret_token = token.encode()
    generated_signature = "sha1=%s" % hmac.new(secret_token, body.encode(), hashlib.sha1).hexdigest()
    return generated_signature


if __name__ == "__main__":
    send_webhook()

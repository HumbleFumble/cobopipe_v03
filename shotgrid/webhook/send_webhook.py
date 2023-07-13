import requests
import json
import os
import hmac
import hashlib

token = '97806dc14d1045b4adabbbb7fd90f193'

def send_webhook(data, vpn=False):
    url = "http://192.168.0.4:21224/remote"
    
    if not vpn:
        url = "http://178.249.49.18:21224/remote"
        
    headers = {'content-type': 'application/json; charset=utf-8'}
    body = json.dumps(data)
    headers['signature'] = generate_signature(body)
    try:
        requests.post(url, json=data, headers=headers)
    except WindowsError as e:
        if '[WinError 10060]' in str(e):
            print(f"Exception: {e}\n\n>> Check if Listener is closed on Application Server. <<\n\n")
    except Exception as e:
        print(f'Exception: {e}')


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
    send_webhook({'Test': 'This is a test string'})

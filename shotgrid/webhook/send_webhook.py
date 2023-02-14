import requests
import json
import os


def send_webhook():
    url = "http://192.168.0.4:8080/webhook"
    path = os.path.abspath(os.path.join(__file__, '..', 'data.json'))
    data = get_json(path)
    requests.post(url, json=data)


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


if __name__ == "__main__":
    send_webhook()

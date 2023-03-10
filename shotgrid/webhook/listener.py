import sys
import os
path = os.path.abspath(os.path.join(__file__, '../../..'))
if path not in sys.path:
    sys.path.append(path)
from flask import Flask, request
from waitress import serve
import shotgrid.webhook.handler as handler
import hmac
import hashlib

app = Flask(__name__)
token = '97806dc14d1045b4adabbbb7fd90f193'


@app.route("/")
def index():
    return """
<body style="background-color: #f2f2f2;">
    <div style="display: grid; grid-template-columns: 1fr; grid-tempalte-rows: 100vh; align-items: center; justify-items: center">
        <h1 style="margin-top: 100px;font-family:Helvetica;background-color: #55a4c1;color: white;padding: 20px;border-radius: 20px;filter: drop-shadow(0px 3px 2px #36589a);">
            Webhook Listener is currently running. 
        </h1>
    </div>
</body>"""


@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        signature = request.headers.get('X-Sg-Signature')
        if validate_secret_token(request, signature):
            webhook_id = request.headers.get('X-Sg-webhook-id')
            data = request.json.get("data")
            timestamp = request.json.get("timestamp")
            handler.run(webhook_id, data, timestamp)
            return "Webhook received and processed."
        else:
            return "Token validation failed."

@app.route("/remote", methods=["POST"])
def remote():
    if request.method == "POST":
        signature = request.headers.get('signature')
        if validate_secret_token(request, signature):
            print(request.json)
            return "Webhook received and processed."
        else:
            return "Token validation failed."
            


def validate_secret_token(request, signature):
    # DO NOT TOUCH - PLEASE
    body = request.data
    secret_token = token.encode()
    generated_signature = "sha1=%s" % hmac.new(secret_token, body, hashlib.sha1).hexdigest()
    if hmac.compare_digest(signature, generated_signature):
        return True
    return False


def deploy(dev=False):
    port = 21224
    if os.getlogin() == 'mha':
        port = 21225
    if os.getlogin() == 'cg':
        port = 21226
    if dev:
        app.run(host="0.0.0.0", port=port)
    else:
        serve(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    if os.getlogin() in ['mha', 'cg']:
        deploy(dev=True)
    else:
        deploy(dev=False)
from flask import Flask, request
from waitress import serve
import shotgrid.webhook.wh_handler as wh_handler
import json

app = Flask(__name__)
# app.secret_key = '97806dc14d1045b4adabbbb7fd90f193'


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
        data = request.json.get("data")
        timestamp = request.json.get("timestamp")
        wh_handler.run(data, timestamp)
        return "Webhook received!"
    

def deploy(dev=False):
    if dev:
        app.run(host="0.0.0.0", port=8080)
    else:
        serve(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    deploy(dev=True)

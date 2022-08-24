#載入LineBot所需要的模組
import json
import re
import os
import pandas
import numpy as np
from flask import *
from datetime import datetime
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *

app = Flask(__name__)

# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi('EFaaQXDQoCQOpmUDUzp3I7Q6sUfs9Y5DFpVu1Ifv5RvbKlEA4nR0Afd0wDxp+OVRpjz0pZNmx7ZAn613wTJwhhpcNH627Cu1g4EqHAs9xm+3C1IExk90Vc9z0b32sKddCf2rfD2kl5nh6gywjc1JjAdB04t89/1O/w1cDnyilFU=')

# 必須放上自己的Channel Secret
handler = WebhookHandler('a7b81bff79cd317a265dd15b56afa313')

@app.route("/", methods=["GET", "POST"])
def callback():
    if request.method == "GET":
        return "Hello Heroku"
    if request.method == "POST":
        signature = request.headers["X-Line-Signature"]
        body = request.get_data(as_text=True)
        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)
        return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    get_message = event.message.text

# Send To Line
    reply = TextSendMessage(text=f"{get_message}")
    line_bot_api.reply_message(event.reply_token, reply)
    
#主程式
import os if __name__ == "__main__":
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)

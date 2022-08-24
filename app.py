#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#載入LineBot所需要的模組
import json
import re
import pandas
import numpy as np
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *

app = Flask(__name__)

# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi('EFaaQXDQoCQOpmUDUzp3I7Q6sUfs9Y5DFpVu1Ifv5RvbKlEA4nR0Afd0wDxp+OVRpjz0pZNmx7ZAn613wTJwhhpcNH627Cu1g4EqHAs9xm+3C1IExk90Vc9z0b32sKddCf2rfD2kl5nh6gywjc1JjAdB04t89/1O/w1cDnyilFU=')

# 必須放上自己的Channel Secret
handler = WebhookHandler('a7b81bff79cd317a265dd15b56afa313')

#line_bot_api.push_message('Ud0b91488c829a40a43d1c5c95050540e', TextSendMessage(text='你可以開始了'))

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
　　# get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
　　# get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
　　# handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

#訊息傳遞區塊
##### 基本上程式編輯都在這個function #####

def Gender():
    gender = input('請輸入性別（男/女）：')
    while gender not in {'男','女'}:
        line_bot_api.reply_message('<reply_token>', TextSendMessage('輸入錯誤'))
        gender = input('請輸入性別（男/女）：')
    return gender

def Height():
    height = input('請輸入身高（公分）：')
    while height.isdigit() == False:
        line_bot_api.reply_message('<reply_token>', TextSendMessage('輸入錯誤'))
        height = input('請重新輸入身高（公分）：')
    return int(height)

def Weight():
    weight = input('請輸入體重（公斤）：')
    while weight.isdigit() == False:
        line_bot_api.reply_message('<reply_token>', TextSendMessage('輸入錯誤'))
        weight = input('請重新輸入體重（公斤）：')
    return int(weight)

def Acitivity():
    acitivity = input('請輸入平日工作量（輕度/中度/重度）:')
    while acitivity not in {'輕度','中度','重度','輕','中','重'}:
        line_bot_api.reply_message('<reply_token>', TextSendMessage('輸入錯誤'))
        acitivity = input('請輸入平日工作量（輕度/中度／重度）:')
    return acitivity

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    if '開啟機器人' in message:
        try:
            Gender()
            Height()
            Weight() 
            Acitivity()
        except LineBotApiError:
            line_bot_api.reply_message('<reply_token>', TextSendMessage('資料未順利傳輸'))
        else:
            line_bot_api.reply_message('<reply_token>', TextSendMessage('資料已輸入完成'))
    
#主程式
import os if __name__ == "__main__":
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)


#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import json, re, gspread, time
import pandas as pd
import numpy as np
from flask import Flask, request, abort
from tabulate import tabulate
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage
from Caculations import DailyCalories, BMI

app = Flask(__name__)

#Line Bot驗證
line_bot_api = LineBotApi("EFaaQXDQoCQOpmUDUzp3I7Q6sUfs9Y5DFpVu1Ifv5RvbKlEA4nR0Afd0wDxp+OVRpjz0pZNmx7ZAn613wTJwhhpcNH627Cu1g4EqHAs9xm+3C1IExk90Vc9z0b32sKddCf2rfD2kl5nh6gywjc1JjAdB04t89/1O/w1cDnyilFU=")    
handler = WebhookHandler("a7b81bff79cd317a265dd15b56afa313")

#Google Sheets驗證
creds = gspread.service_account(filename='calorieslinebot-36b94fbce9d8.json')
client = creds.open_by_url("https://docs.google.com/spreadsheets/d/19SYKV2NVmluHuCrh_4150VE7CLnPM_6gR68qWgjb9sM/edit#gid=0")   

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback(request):
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    print(body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

#設定LINE Bot回覆訊息
def line_reply(event, msg_text):
    line_bot_api.reply_message(
        event.reply_token,
        TextMessage(text=msg_text, type="text"))    
    
def get_gsheet(index_num):
    sheet = client.get_worksheet(index_num)
    return sheet

def now_time():
    now = time.localtime()
    timeString = time.strftime("%Y-%m-%d %H:%M:%S", now)
    return timeString   

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    txt = event.message.text #取得使用者輸入的文字
    user_id = str(event.source.user_id) #取得使用者的id
    insert_time = now_time() #取得輸入的時間
    info_sheet = get_gsheet(0)
    food_sheet = get_gsheet(1)
    exer_sheet = get_gsheet(2)
    user_gsheet_name = user_id[:11]

    if re.search(',',txt) != None:
        if user_id not in info_sheet.col_values(2):
            height = (re.search('(\d+)公分',txt) or re.search('(\d+)cm',txt)).group(1)
            weight = (re.search('(\d+)公斤',txt) or re.search('(\d+)kg',txt)).group(1)
            activity = re.search('[輕中重]',txt).group()
            try:
                info_sheet.append_row([insert_time,user_id,height,weight,activity])
                user_gsheet = client.add_worksheet(title=user_gsheet_name, rows=1000, cols=20)
                titles = ['time','user_id','食物項目','增加熱量','運動項目','消耗熱量','今日剩餘熱量']
                user_gsheet.append_row(titles)
                line_reply(event,'基本資料已填寫成功')
            except:
                line_reply(event,'基本資料未填寫成功')
        else:
            line_reply(event,'您已有填寫基本資料\n如有需修改，請一次輸入一項欲修改的項目\n如「修改身高 170cm」')
    
    elif re.match('修改',txt) != None:
        row = info_sheet.find(user_id).row
        try:
            if re.search('身高',txt) != None:
                try:
                    height = (re.search('(\d+)公分',txt) or re.search('(\d+)cm',txt)).group(1)
                    info_sheet.update_acell('C'+str(row),height)
                    line_reply(event,'身高已修改成功')
                except:
                    line_reply(event,'身高未修改成功')
            if re.search('體重',txt) != None:
                try:
                    weight = (re.search('(\d+)公斤',txt) or re.search('(\d+)kg',txt)).group(1)
                    info_sheet.update_acell('D'+str(row),weight)
                    line_reply(event,'體重已修改成功')
                except:
                    line_reply(event,'體重未修改成功')
            if re.search('活動量',txt) != None:
                try:
                    activity = re.search('[輕中重]',txt).group()
                    info_sheet.update_acell('E'+str(row),activity)
                    line_reply(event,'活動量已修改成功')
                except:
                    line_reply(event,'活動量未修改成功')
        except:
            line_reply(event,'資料未傳輸成功')

    elif txt == '查看個人資料':
        row = info_sheet.find(user_id).row
        info = info_sheet.row_values(row)
        height = info[2]
        weight = info[3]
        activity = info[4]
        bmi, comment = BMI(int(height),int(weight))
        DC = DailyCalories(int(height),int(weight),activity)
        information = '身高為：'+str(height)+'\n體重為：'+str(weight)+'\n活動量為：'+activity+'\nBMI為'+str(bmi)+'\n建議每日攝取熱量為'+str(DC)+'大卡'
        try:
            line_reply(event,information)
        except:
            line_reply(event,'顯示失敗，個人資料可能有缺漏或有誤')

    elif re.match('查詢',txt) != None:
        search_name = re.search('查詢(.+)',txt).group(1)
        if search_name in food_sheet.col_values(1):
            row = food_sheet.find(search_name).row
            calory = food_sheet.row_values(row)
            calory_str = ' '.join(calory)+'大卡'
            line_reply(event,'您查詢的是：\n'+calory_str)
        elif search_name in exer_sheet.col_values(1):
            row = exer_sheet.find(search_name).row
            exercise = exer_sheet.row_values(row)
            exercise_str = exercise[0]+' 每小時每公斤消耗'+exercise[1]+'大卡'
            line_reply(event,exercise_str)
        else:
            line_reply(event,'查詢失敗，資料庫並無此項目')
    
    elif re.match('新增',txt) != None:
        user_gsheet = client.worksheet(user_gsheet_name)
        search_name = re.search('新增(.+)/',txt).group(1)
        number = re.search('/([\d.]+)',txt).group(1)
        if search_name in food_sheet.col_values(1):
            c_row = food_sheet.find(search_name).row
            calory = food_sheet.row_values(c_row)
            calories = str(float(calory[3])*float(number))
            user_gsheet.append_row([insert_time,user_id,search_name,calories,'-',0])
            line_reply(event,'已新增完成')
        elif search_name in exer_sheet.col_values(1):
            c_row = exer_sheet.find(search_name).row
            calory = exer_sheet.row_values(c_row)[1]
            w_row = info_sheet.find(user_id).row
            weight = info_sheet.row_values(w_row)[3]
            calories = float(calory)*float(weight)*float(number)
            user_gsheet.append_row([insert_time,user_id,'-',0,search_name,calories])
            line_reply(event,'已新增完成')
        else:
            line_reply(event,'資料庫並無此項目')
    
    elif txt == '查看本日熱量資料':
        user_gsheet = client.worksheet(user_gsheet_name)
        today = now_time()[:11]
        col_values_list = user_gsheet.col_values(1)
        #pd.set_option('display.unicode.ambiguous_as_wide',True)
        #pd.set_option('display.unicode.east_asian_width',True)
        row_num = []
        for i in col_values_list:
            if today in i:
                row_num.append(col_values_list.index(i))
        if len(row_num) != 0:
            row_values_list = user_gsheet.get_all_values()[row_num[0]:row_num[-1]+1]
            index_num = [str(i) for i in range(1,len(row_num)+1)]
            record = pd.DataFrame(row_values_list, index=index_num,columns=['time','user_id','食物名','＋熱量','運動名','－熱量'])
            daily_record = record[['食物名','＋熱量','運動名','－熱量']]
            food_calo = record[:]['＋熱量'].apply(float).sum()
            exer_calo = record[:]['－熱量'].apply(float).sum()
            info_row = info_sheet.find(user_id).row
            info = info_sheet.row_values(info_row)
            height = info[2]
            weight = info[3]
            activity = info[4]
            bmi, comment = BMI(int(height),int(weight))
            DC = float(DailyCalories(int(height),int(weight),activity))
            DC_now = DC - food_calo + exer_calo
            try:
                line_bot_api.reply_message(
                event.reply_token, [
                TextSendMessage(text=daily_record.to_string()),
                TextSendMessage('每日建議攝取'+str(DC)+'大卡'),
                TextSendMessage('本日共增加'+str(food_calo)+'大卡'),
                TextSendMessage('本日共消耗'+str(exer_calo)+'大卡'),
                TextSendMessage('本日剩餘'+str(DC_now)+'大卡')])
            except:
                line_reply(event,'無法成功列印')
        else:
            line_reply(event,'今天還沒有紀錄喔！')
        
    else:
        line_reply(event,'我不清楚您在說什麼，請確認輸入格式')
                
if __name__ == "__main__":
    app.run(host='0.0.0.0')


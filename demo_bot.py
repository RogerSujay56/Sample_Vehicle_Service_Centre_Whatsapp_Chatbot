from flask import Flask
from flask import jsonify
from flask import request
import requests
import http.client
import json
from time import sleep
from datetime import datetime, date, timedelta
import base64
import os
import io
import re
import boto3
import math
import pymysql
import http.server
import random
import string
import urllib3
import subprocess
import urllib



urllib3.disable_warnings (urllib3.exceptions.InsecureRequestWarning)

app = Flask (__name__)

aws_host = 'birdwabs.cc6s9j3sk8vb.ap-south-1.rds.amazonaws.com'
usr = "admin"
pas = "your_password"
db = "Sujay_BVC_Demo"



def get_connection(query,val):
    cnx = pymysql.connect (user=usr, max_allowed_packet=1073741824, password=pas, host=aws_host,database=db)
    cursor = cnx.cursor ()
    cursor.execute (query, val)
    cnx.commit ()
    cnx.close ()


def update_authkey() :
    url = "https://3.108.41.139:9090/v1/users/login"
    # url = "https://3.80.233.18:9090/v1/users/login"
    
    payload = "{\n\t\"new_password\": \"Khairnar@123\"\n}"
    headers = {
        'Content-Type' : 'application/json',
        'Authorization' : 'Basic <base64(username:password)>',
        'Authorization' : 'Basic YWRtaW46S2hhaXJuYXJAMTIz'
    }
    response = requests.request ("POST", url, headers=headers, data=payload, verify=False)
    rs = response.text
    json_data = json.loads (rs)
    return json_data["users"][0]["token"]

authkey = update_authkey ()

def send_message(to, body, message) :
    authkey = update_authkey ()
    url="https://3.108.41.139:9090/v1/messages"
    # url = "https://3.80.233.18:9090/v1/messages"

    payload = "{\n  \"to\": \"" + to + "\",\n  \"type\": \"text\",\n  \"recipient_type\": \"individual\",\n  \"text\": {\n    \"body\": \" " + body + " \"\n  }\n}\n"

    headers = {
        'Content-Type' : "application/json",
        'Authorization' : "Bearer " + authkey,
        'User-Agent' : "PostmanRuntime/7.20.1",
        'Accept' : "*/*",
        'Cache-Control' : "no-cache",
        'Postman-Token' : "44d01f0f-a3a5-49a7-9b1f-2e2ef88f62bd",
        # 'Host': "3.230.123.214:9090",
        'Host': "54.198.53.204:9090",
        'Accept-Encoding' : "gzip, deflate",
        'Content-Length' : "116",
        'Connection' : "keep-alive",
        'cache-control' : "no-cache"
    }
    try :
        response = requests.request ("POST", url, data=payload.encode('utf-8'), headers=headers, verify=False)
        print(response)
    except Exception as e :
        print (e)
    statuscode = response.status_code
    response = response.text
    savesentlog(to, response, statuscode,message,'text')
    return response


def save_message_status(response) :
    response = response
    message_or_status_id = response["statuses"][0]["id"]
    sender_id = response["statuses"][0]["recipient_id"]
    status = response["statuses"][0]["status"]
    timestamp1 = datetime.fromtimestamp (int (response["statuses"][0]["timestamp"]))
    add_data = "UPDATE tbl_logs SET status = (%s), last_updateddate = (%s) where message_id = '"+message_or_status_id+"'"
    val = (status,timestamp1)
    try :
        cnx = pymysql.connect (user=usr, max_allowed_packet=1073741824, password=pas, host=aws_host,
                        database=db)  # make changes
        cursor = cnx.cursor ()
        cursor.execute (add_data, val)
        cnx.commit ()
        cnx.close ()
    except Exception as a :
        print (a)

def savesentlog(frm, response, statuscode,Body,msgtype):
    statuscode = str(statuscode)
    response = json.loads(response)
    message_id = str(response["messages"][0]["id"])
    add_data = "insert into tbl_logs(type_of_response, sender_id, message_id, status,messagebody,camp_name,type_of_message) values (%s,%s,%s,%s,%s,%s,%s)"
    val = (str(response),frm, message_id, statuscode,Body,"demo_rb",msgtype)
    cnx = pymysql.connect (user=usr, max_allowed_packet=1073741824, password=pas, host=aws_host,database=db)
    cursor = cnx.cursor ()
    cursor.execute (add_data, val)
    cnx.commit ()
    cnx.close ()

def send_pdf(to, link, caption=""):
    authkey = update_authkey ()
    url = "https://3.108.41.139:9090/v1/messages/"

    payload = "{\n\t\"to\": \""+to+"\",\n\t\"type\": \"document\",\n\t\"recipient_type\": \"individual\",\n\t\"document\": {\n\t\t\"link\": \""+link+"\",\n\t\t\"caption\": \""+caption+"\"\n\t}\n}\n"
    headers = {
        'Content-Type': "application/json",
        'Authorization': "Bearer "+authkey,
        'cache-control': "no-cache",
        'Postman-Token': "1083c9be-a60e-4a0d-94a4-448ef126085e"
        }

    response = requests.request("POST", url, data=payload, headers=headers, verify = False)
    print(response.text)
    return response

def already_exist(frm,today):
    add_data = "select id from tbl_cust where mobile_number = '" +frm+ "'"
    cnx = pymysql.connect(user=usr, max_allowed_packet= 1073741824, password=pas, host=aws_host, database=db)
    cursor = cnx.cursor ()
    cursor.execute (add_data)
    records = cursor.fetchone ()
    print(records)
    cnx.commit ()
    cnx.close ()
    if  records == None or list(records)[0] == None:
        return False
    else :
        return True

def next_day(frm,today):
    add_data = "select id from tbl_cust where mobile_number = '" +frm+ "' and date(created_date) = '"+today+"' limit 1"
    cnx = pymysql.connect(user=usr, max_allowed_packet= 1073741824, password=pas, host=aws_host, database=db)
    cursor = cnx.cursor ()
    cursor.execute (add_data)
    records = cursor.fetchone ()
    print(records)
    cnx.commit ()
    cnx.close ()
    if  records == None or list(records)[0] == None:
        return False
    else :
        return True

def daily_entry_count(frm,today):

    add_data = "select count(id) from tbl_participants where mobile_number = "+frm+" and date(created_date)='"+today+"'"
    cnx = pymysql.connect(user=usr, max_allowed_packet= 1073741824, password=pas, host=aws_host, database=db)
    cursor = cnx.cursor ()
    cursor.execute (add_data)
    records = cursor.fetchone ()
    cnx.commit()
    cnx.close()
    if records == None or list(records)[0] == None:
        count = '0'
    else:
        count = list(records)[0]
        count = str(count)
    return count

def interactive_message_with_2button(to,body,option1,option2,message):
    authkey = update_authkey ()
    url="https://3.108.41.139:9090/v1/messages"
    payload = json.dumps({
    "to": to,
    "recipient_type": "individual",
    "type": "interactive",
    "interactive": {
        "type": "button",
        "body": {
            "text": body
            },
        "action": {
            "buttons": [
            {
                "type": "reply",
                "reply": {
                    "id": "1",
                    "title": option1
                }
            },
                {
                "type": "reply",
                "reply": {
                    "id": "2",
                    "title": option2
                }
                }
        ]
        }
    }
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+authkey
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    print(response.text)
    statuscode = response.status_code
    response = response.text
    savesentlog(to, response, statuscode,message,'interactive')
    return response

def interactive_message_with_1button(to,body,bt_id,option1,message):
    authkey = update_authkey ()
    url="https://3.108.41.139:9090/v1/messages"
    payload = json.dumps({
    "to": to,
    "recipient_type": "individual",
    "type": "interactive",
    "interactive": {
        "type": "button",
        "body": {
            "text": body
            },
        "action": {
            "buttons": [
            {
                "type": "reply",
                "reply": {
                    "id": bt_id,
                    "title": option1
                }
            }
        ]
        }
    }
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+authkey
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    print(response.text)
    statuscode = response.status_code
    response = response.text
    savesentlog(to, response, statuscode,message,'interactive')
    return response

def interactive_message_with_3button(to,body,option1,option2,option3,message):
    authkey = update_authkey ()
    url="https://3.108.41.139:9090/v1/messages"
    payload = json.dumps({
    "to": to,
    "recipient_type": "individual",
    "type": "interactive",
    "interactive": {
        "type": "button",
        "body": {
            "text": body
            },
        "action": {
            "buttons": [
            {
                "type": "reply",
                "reply": {
                    "id": "1",
                    "title": option1
                }
            },
            {
                "type": "reply",
                "reply": {
                    "id": "2",
                    "title": option2
                }
            },
            {
                "type": "reply",
                "reply": {
                    "id": "3",
                    "title": option3
                }
            }
        ]
        }
    }
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+authkey
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    print(response.text)
    statuscode = response.status_code
    response = response.text
    savesentlog(to, response, statuscode,message,'interactive')
    return response

def disable_other_buttons(payload, message_id):
    authkey = update_authkey()
    url = f"https://3.108.41.139:9090/v1/messages/{message_id}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + authkey
    }
    response = requests.get(url, headers=headers, verify=False)
    message = json.loads(response.text)
    buttons = message['interactive']['action']['buttons']
    for button in buttons:
        if button['reply']['title'] != payload:
            button['reply']['disabled'] = True
    payload = json.dumps({
        "interactive": {
            "type": "button",
            "action": {
                "buttons": buttons
            }
        }
    })
    response = requests.patch(url, headers=headers, data=payload, verify=False)
    print(response.text)

def send_interactive_menu(frm,head,body,title,item1,item2,item3,item4,item5,item6,item7,desc1,desc2,desc3,desc4,desc5,desc6,desc7,message):
    authkey = update_authkey ()
    url="https://3.108.41.139:9090/v1/messages"
    payload = json.dumps({
    "to": frm,
    "recipient_type": "individual",
    "type": "interactive",
    "interactive":{
    "type": "list",
    "header": {
      "type": "text",
      "text": head
    },
    "body": {
      "text": body
    },
    "action": {
      "button": title,
      "sections":[
        {
          "rows": [
            {
              "id":"1",
              "title": item1,
              "description": desc1,           
            }
            ,
            {
                "id":"2",
                "title": item2,
                "description": desc2, 
            },
            {
                "id":"3",
                "title": item3,
                "description": desc3, 
            }
            ,
            {
                "id":"4",
                "title": item4,
                "description": desc4, 
            },
            {
                "id":"5",
                "title": item5,
                "description": desc5, 
            }
            ,
            {
                "id":"6",
                "title": item6,
                "description": desc6, 
            },
            {
                "id":"7",
                "title": item7,
                "description": desc7, 
            }
          ]
        },
        
      ]
    }
  }
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+authkey
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    statuscode = response.status_code
    response = response.text
    print(response)
    savesentlog(frm, response, statuscode,message,'interactive')
    return response

def send_texturl(to, body, message):
    authkey = update_authkey ()
    url = "https://3.108.41.139:9090/v1/messages"

    payload = json.dumps({
    "to": ""+to+"",
    "type": "text",
    "text": {
        "body": ""+body+""
    },
    "preview_url": True
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+authkey
    }

    try :
        response = requests.request ("POST", url, data=payload.encode("utf-8"), headers=headers, verify=False)
        print(response.text)
    except Exception as e :
        print (e)
    statuscode = response.status_code
    response = response.text
    savesentlog(to, response, statuscode,message,'text')
    return response











#demobot class

class demobot:
    def __init__(self,frm=None,resp1=None,msg_type=None,image_data=None,response=None):
        if frm!=None:
            self.frm = frm
        if resp1!=None:
            self.resp1 = resp1
        if msg_type!=None:
            self.msg_type = msg_type
        if image_data!=None:
            self.image_data = image_data
        if response!=None:
            self.response = response

    def eng(self):
        frm= self.frm
        msg_type = self.msg_type
        resp1 = self.resp1
        image_data = self.image_data
        response = self.response
        today = str(date.today())
        now = str (datetime.now ())
        
        print(resp1)
        cnx = pymysql.connect (user=usr, max_allowed_packet=1073741824, password=pas, host=aws_host, database=db)
        check_already_valid = "SELECT lang, is_lang,is_valid,is_info,id,is_verified,main_menu,sub_menu,resp1,is_temp,serv_no from tbl_whatsapp where mobile_number = '" +frm+ "'"
        cursor = cnx.cursor ()
        cursor.execute (check_already_valid)
        result = cursor.fetchone()
        cnx.commit ()
        cnx.close ()
        if result == None:
            lang = '0'
            is_lang = '0'
            is_valid = '0'
            is_info = '0'
            wa_id = '0'
            is_verified = '0'
            main_menu = '0'
            sub_menu = '0'
            em_resp1 = '0'
            is_temp ='0'
            serv_no ='0'


        else:
            result = list(result)
            lang = result[0]
            is_lang = result[1]
            is_valid = result[2]
            is_info = result[3]
            wa_id = str(result[4])
            is_verified = str(result[5])
            main_menu = str(result[6])
            sub_menu = str(result[7])
            em_resp1 = str(result[8])
            is_temp= str(result[9])
            serv_no= str(result[10])

        print(is_valid)
        # notify_user()
        if (msg_type == "text" or msg_type == 'button' or msg_type == 'interactive'):
            print(resp1,'======')
            print(is_temp)
            if is_temp =='0':
                menu = 'To Book a Service,Please select any one service from the below options.'
                interactive_message_with_3button(frm,menu,'Car Wash','Engine Oil','Overall Service','Ask_Service')
                # sleep(1)
                print("interactive 3 button")
                update_name = "UPDATE tbl_whatsapp set is_temp = (%s), main_menu = (%s), sub_menu = (%s), is_valid = (%s) where mobile_number = '" +frm+ "' "
                val = ('11','0','0','0')
                get_connection(update_name,val)
                main_menu ='0'
                sub_menu = '0'
                is_valid = '0'
                # is_temp = '11'

            elif is_temp == '11': #define menu options
                print("inside istemp 11")
                if resp1 in ['Car Wash','Engine Oil','Overall Service']:

                    print("inside isinfo 11 inside first if")
                    add_service = "Insert into tbl_service (service_type) values (%s)"
                    val1 = (resp1)
                    get_connection(add_service, val1)

                    send_message(frm,"You have selected option of "+resp1,"servicetype")

                

                    now = datetime.now()
                    dates = []
                    while len(dates) < 7:
                        next_date = now + timedelta(days=1)
                        if next_date.weekday() < 5:  # Only include weekdays (Monday=0, Sunday=6)
                            dates.append(next_date.strftime("%Y/%m/%d %A"))
                        now = next_date

                    # msg='Select Date from below option\\n\\n'
                    # msg += 'Here are the next three weekday dates available:\\n\\n'
                    # msg += '\\n'.join(f'{i+1}. {date}' for i, date in enumerate(dates))
                    # msg += '\\n\\nPlease select a date by typing in the corresponding number:'
                                                                            
                                      
                    
                    head='DATE SELECTION'
                    body='Select Date from the below list of available dates'
                    title= 'Date and Day'
                    # item1= dates[0].split(' ')[0]
                    # item2= dates[1].split(' ')[0]
                    # item3= dates[2].split(' ')[0]
                    # item4= dates[3].split(' ')[0]
                    # item5= dates[4].split(' ')[0]
                    # item6= dates[5].split(' ')[0]
                    # item7= dates[6].split(' ')[0]
                    # desc1= "Day: "+dates[0].split(' ')[1]
                    # desc2= "Day: "+dates[1].split(' ')[1]
                    # desc3= "Day: "+dates[2].split(' ')[1]
                    # desc4= "Day: "+dates[3].split(' ')[1]
                    # desc5= "Day: "+dates[4].split(' ')[1]
                    # desc6= "Day: "+dates[5].split(' ')[1]
                    # desc7= "Day: "+dates[6].split(' ')[1]

                    # dates = ['03/30/2023 Thursday', '03/31/2023 Friday', '04/03/2023 Monday', '04/04/2023 Tuesday', '04/05/2023 Wednesday', '04/06/2023 Thursday', '04/07/2023 Friday']
                    items = [date.split()[0] for date in dates]
                    desc = ["Day: " + date.split()[1] for date in dates]
                    send_interactive_menu(frm, head, body, title, *items, *desc, 'datemenulist')

                    
                    # send_interactive_menu(frm,head,body,title,item1,item2,item3,item4,item5,item6,item7,desc1,desc2,desc3,desc4,desc5,desc6,desc7,'datemenulist')

                    #response to number format to set main menu
                    if resp1 == 'Car Wash':
                        resp1 = '1'
                    elif resp1 == 'Engine Oil':
                        resp1 = '2'
                    elif resp1 == 'Overall Service':
                        resp1 = '3'
                                                    
                   
                    update_name = "UPDATE tbl_whatsapp set main_menu = (%s), is_temp= (%s),serv_no=(%s) where mobile_number = '" +frm+ "' "
                    val = (resp1,'22',resp1)
                    get_connection(update_name, val)
                
                    
                    main_menu = resp1
                    print(main_menu)
                    
                else:
                    send_message(frm, 'select a valid Menu option','menu_validation')

            elif is_temp =="22" and serv_no=='1':
                print("inside temp 22 and servno1")

                if main_menu == '1' and is_valid == '0':

                    print("inside main_menu == '1' and is_valid == '0'")

                    print("Hi entered inside temp 22 and serv no "+ resp1,"check")
                    #store this resp1 in table booking booking date
                    add_date = "Insert into tbl_booking (booking_date) values (%s)"
                    val1 = (resp1)
                    get_connection(add_date, val1)
                    
                    interactive_message_with_2button(frm,"We have only two slots available select any one \\nSlot1: 09:00 AM to 12:00 PM \\nSlot2: 01:00 PM to 06:00 PM ","Slot1","Slot2","slot_selection")
                    
                    print('below interactive2button'+resp1)

                    update_name = "UPDATE tbl_whatsapp set main_menu = (%s) where mobile_number = '" +frm+ "' "
                    val = ('2')
                    get_connection(update_name, val)
                
                if main_menu == '2' and is_valid == '0':

                    print('inside mainmenu 2 and isvalid 0')

                    if resp1 == 'Slot1':
                        resp1 = '1'
                    elif resp1 == 'Slot2':
                        resp1 = '2'

                    # send_message(frm,"You have selected the "+ resp1,"slotnumber")
                    send_message(frm,"Confirm Your Booking? Type Y/n?",'confirmation')
                                    
                    add_service = "Insert into tbl_slot (slot_number) values (%s)"
                    val1 = (resp1)
                    get_connection(add_service, val1)
                    
                    update_name = "UPDATE tbl_whatsapp set is_temp = (%s) where mobile_number = '" +frm+ "' "
                    val = ('33')
                    get_connection(update_name,val)
                                   
                                                
                    # interactive_message_with_2button(frm,"Choose available slots for *Car Wash* from below","Slot1","Slot2","slot_selection")
                           
                
            elif is_temp =="22" and serv_no=='2':
                print("inside temp 22 and servno2")

                if main_menu == '2' and is_valid == '0':

                    print("inside main_menu == '2' and is_valid == '0'")

                    print("Hi entered inside temp 22 and serv no "+ resp1,"check")
                    #store this resp1 in table booking booking date
                    add_date = "Insert into tbl_booking (booking_date) values (%s)"
                    val1 = (resp1)
                    get_connection(add_date, val1)
                    
                    interactive_message_with_2button(frm,"We have only two slots available select any one \\nSlot1: 09:00 AM to 12:00 PM \\nSlot2: 01:00 PM to 06:00 PM ","Slot1","Slot2","slot_selection")
                    
                    print('below interactive2button'+resp1)

                    update_name = "UPDATE tbl_whatsapp set main_menu = (%s) where mobile_number = '" +frm+ "' "
                    val = ('3')
                    get_connection(update_name, val)
                
                if main_menu == '3' and is_valid == '0':

                    print('inside mainmenu 3 and isvalid 0')

                    if resp1 == 'Slot1':
                        resp1 = '1'
                    elif resp1 == 'Slot2':
                        resp1 = '2'

                    # send_message(frm,"You have selected the "+ resp1,"slotnumber")
                    send_message(frm,"Confirm Your Booking? Type Y/n?",'confirmation')
                                    
                    add_service = "Insert into tbl_slot (slot_number) values (%s)"
                    val1 = (resp1)
                    get_connection(add_service, val1)
                    
                    update_name = "UPDATE tbl_whatsapp set is_temp = (%s) where mobile_number = '" +frm+ "' "
                    val = ('33')
                    get_connection(update_name,val)


            elif is_temp =="22" and serv_no=='3':
                print("inside temp 22 and servno3")

                if main_menu == '3' and is_valid == '0':

                    print("inside main_menu == '3' and is_valid == '0'")

                    print("Hi entered inside temp 22 and serv no "+ resp1,"check")
                    #store this resp1 in table booking booking date
                    add_date = "Insert into tbl_booking (booking_date) values (%s)"
                    val1 = (resp1)
                    get_connection(add_date, val1)
                    
                    interactive_message_with_2button(frm,"We have only two slots available select any one \\nSlot1: 09:00 AM to 12:00 PM \\nSlot2: 01:00 PM to 06:00 PM ","Slot1","Slot2","slot_selection")
                    
                    print('below interactive2button'+resp1)

                    update_name = "UPDATE tbl_whatsapp set main_menu = (%s) where mobile_number = '" +frm+ "' "
                    val = ('4')
                    get_connection(update_name, val)
                
                if main_menu == '4' and is_valid == '0':

                    print('inside mainmenu 4 and isvalid 0')

                    if resp1 == 'Slot1':
                        resp1 = '1'
                    elif resp1 == 'Slot2':
                        resp1 = '2'

                    # send_message(frm,"You have selected the "+ resp1,"slotnumber")
                    send_message(frm,"Confirm Your Booking? Type Y/n?",'confirmation')
                                    
                    add_service = "Insert into tbl_slot (slot_number) values (%s)"
                    val1 = (resp1)
                    get_connection(add_service, val1)
                    
                    update_name = "UPDATE tbl_whatsapp set is_temp = (%s) where mobile_number = '" +frm+ "' "
                    val = ('33')
                    get_connection(update_name,val)        

            elif is_temp =='33' and resp1.lower() =='y':

                # cnx = pymysql.connect (user=usr, max_allowed_packet=1073741824, password=pas, host=aws_host, database=db)
                # cursor = cnx.cursor ()
                # get_name = "SELECT name from tbl_customer where mobile_number = '" +frm+ "'"
                # cursor.execute (get_name)
                # name = cursor.fetchone()
                # get_servicestation= "SELECT stn_no from tbl_whatsapp where mobile_number = '" +frm+ "'" 
                # cursor.execute (get_servicestation)
                # service_station = cursor.fetchone()
                # get_service= "SELECT service_type from tbl_service where mobile_number = '" +frm+ "'" 
                # cursor.execute (get_service)
                # service = cursor.fetchone()
                # get_bookingdate= "SELECT booking_date from tbl_booking where mobile_number = '" +frm+ "'"  #make mobile no primary key in every table
                # cursor.execute (get_bookingdate)
                # Date = cursor.fetchone()

                # get_slot= "SELECT slot_number from tbl_slot where mobile_number = '" +frm+ "'"  #make mobile no primary key in every table
                # cursor.execute (get_slot)
                # Slot_no = cursor.fetchone()

                

                # cnx.commit ()
                # cnx.close ()
                name='afsdf'
                service_station='1234'
                service='adsfdg'
                Date='12/12/2332'
                Slot_no='123'

                # f'Finally the Booking Message with Date & Time for Confirmation.\n\n'
                # f'Name: {name}\nLocation: {location}\nCategory: {category}\n'
                # f'Date: {dates}\nTime: {time_opt}\n\n Enter Stop or Quit to exit'
                send_message(frm,f"Booking Confirmed \\n Your Booking Details: "
                             f'Name: {name} \\nService_Station:{service_station}\\nService:{service}'
                             f'\\nDate of Booking:{Date}\\nSlot_Number:{Slot_no}','Confirmation')
            
            else:
                send_message(frm,"Enter Valid Response",'invalidconfirmation')
                
            
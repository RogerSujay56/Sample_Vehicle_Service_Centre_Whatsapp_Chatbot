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
from demo_bot import demobot

urllib3.disable_warnings (urllib3.exceptions.InsecureRequestWarning)

app = Flask (__name__)

aws_host = 'birdwabs.cc6s9j3sk8vb.ap-south-1.rds.amazonaws.com'
usr = "admin"
pas = "Birdwabs2019"
db = "Sujay_BVC_Demo"

def get_connection(query,val):
    cnx = pymysql.connect (user=usr, max_allowed_packet=1073741824, password=pas, host=aws_host,database=db)
    cursor = cnx.cursor ()
    cursor.execute (query, val)
    cnx.commit ()
    cnx.close ()

#flow 1
#Pre-define text
email = 'Kindly enter your *Email Id* 📧'
pincode= "Kindly enter your *Pin Code* "
fprocess_complte = '''Thank you for sharing the Information, Well done! *Let's Start by selecting a Option.* '''
storenames = 'Please select near by store 🏤'
deliverytype = 'Kindly select your order fulfillment preference 🛒 by *{}* store.'
selected_ordertype = 'Thank you for sharing your store preference. Click on the Link to Place Your Order for {} 🏤'
menu = 'Please select any one service from the below options.'
query = '📝 Raised your query in Max 300 words or Click on Menu.'
ord_status = 'For order id: {}, created on {} is {}.'
#query_raised = 'Your query Id: *{}*, successfully generated '+thumbsup+', our agent will call you soon.'
#query_raised = 'The Service request Id: *{}* is successfully generated against your query.'+thumbsup+'\\nThe Store Agent will contact you within *next 24* hrs to resolve your request'
query_raised = 'Thank you for *sharing the details*, We have raised the request against your query 👍 \\nYour *service request Id* is *{}*. \\n\\nThe *Store Agent* will contact you within *24 hrs* to resolve it'
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
selfpick = 'Thank you for sharing your order fulfillment preference 🛒.\nYou have opted for *Self Pick up* at *{}* Store.\n\n*Store Timings*\n*Sun - Thu* 8AM to 2PM\n*Fri*: 7AM - 12PM\n*Closed on* Saturday'
#selfpick = 'Thank you for sharing your order fulfillment preference 🛒.\nYou have opted for *Self Pick up* at *{}* Store.\n\n*Store Timings*\n*Sun - Thu* 8AM to 2PM\n*Fri*: 7AM - 12PM\n*Ramadan Time:* 9AM - 3PM\n*Closed on* Saturday'
homedel = 'Thank you for sharing your order fulfillment preference 🛒.\nYou have opted for *Home Delivery* by *{}* Store. 📦 \n\nFor Home Delivery -\n*Order will be delivered within 48 Hrs.*'
#===========================================================================================
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

def send_interactive_menu(frm,head,body,title,item1,item2,item3,desc1,desc2,desc3,message):
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
            },
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


def order_From_exist(wa_id):
    add_data = "select booking_status from tbl_order where wa_id = '"+wa_id+"' order by id desc"
    print(add_data)
    cnx = pymysql.connect(user=usr, max_allowed_packet= 1073741824, password=pas, host=aws_host, database=db)
    cursor = cnx.cursor ()
    cursor.execute (add_data)
    records = cursor.fetchone()
    cnx.commit()
    cnx.close()
    #records = str(list(records)[0])
    print(records)
    if records == None:
        return False
    else:
        records = str(list(records)[0])
        if records == '0':
            return True
        else:
            return False

def download_media(id) :
    authkey = update_authkey ()
    url =  "https://3.108.41.139:9090" + "/v1/media/" + id
 
    headers = {
        'Content-Type' : "application/json",
        'Authorization' : "Bearer " + authkey,
        'cache-control' : "no-cache",
        'Postman-Token' : "c7225772-08c7-43f8-b905-1b18da80d814"
    }
    response = requests.request ("GET", url, headers=headers, verify=False)
    return response



#Bot Started

@app.route ('/', methods=['POST', 'GET'])
def Get_Message() :
    # print ("first entered")
    response = request.json
    statusjson = json.dumps (response, indent=4)
    # print(response)
    try:

        if 'messages' in response :
            frm= str(response["messages"][0]["from"])
            print(frm)
            msg_type = str(response["messages"][0]["type"])
            print(msg_type)
            
            if msg_type == 'button':
                resp1 = response["messages"][0]["button"]["payload"]
                print(resp1)
            else:
                if msg_type == 'text':
                    resp1 = response["messages"][0]["text"]["body"]
                else:
                    resp1 = ''
                    
            if msg_type == 'image':
                print("image if")
                image_data = str(response["messages"][0]["image"]["id"])
            else:
                image_data = '' 

            if msg_type == 'interactive':
                if 'button_reply' in response["messages"][0]["interactive"]:
                    resp1 = response["messages"][0]["interactive"]["button_reply"]["title"]
                    print(resp1)
                elif 'list_reply' in response["messages"][0]["interactive"]:
                    resp1 = response["messages"][0]["interactive"]["list_reply"]["title"]
                    print(resp1) 


            demo_bot = demobot(frm,resp1,msg_type,image_data,response)

    
            today = str(date.today())
            now = str (datetime.now ())
            cnx = pymysql.connect (user=usr, max_allowed_packet=1073741824, password=pas, host=aws_host, database=db)
            check_already_valid = "SELECT camp_id, is_valid from tbl_cust where mobile_number = '" +frm+ "'"
            cursor = cnx.cursor ()
            cursor.execute (check_already_valid)
            result = cursor.fetchone()
            cnx.commit ()
            cnx.close ()
            if result == None:
                camp_id = '0'
                is_valid = '0'
            else:
                result = list(result)
                camp_id = result[0]
                is_valid = result[1]
                
            if (msg_type == 'text' or msg_type == 'button' or msg_type == 'interactive'):

                if resp1.lower()=='test' and is_valid == '0':
               
                    if not already_exist(frm,today):  #New User
                        # print("entered into new user if block")
                        interactive_message_with_2button(frm,"Hello 👋, Welcome to *Vehical Service Centre!* 🤗  \\nTo get started, \\nkindly enter which service station you would like to choose?","Service_Station1","Service_Station2","Station_selection")
                        
                        update_name = "insert into tbl_cust(mobile_number, camp_id,is_valid) values (%s,%s,%s)"
                        val = (frm, '1','1')
                        get_connection(update_name,val)
                        update_name1 = "insert into tbl_whatsapp(mobile_number, created_date,lang) values (%s,%s,%s)"
                        val1 = (frm, today,'1')
                        get_connection(update_name1,val1)
                       
            
                elif (resp1 in ['Service_Station1','Service_Station2','service_station1','service_station2']): # and (already_exist(frm,today)):

                    # print("entered into service station check")
                    #change camp id as per name
                    
                    if resp1 in ['Service_Station1','service_station1']:
                        
                        update_name1 = "UPDATE tbl_whatsapp set stn_no = (%s) where mobile_number = '" +frm+ "' "
                        val1 =('1')
                        get_connection(update_name1,val1)
                        
                    else:
                        
                        update_name1 = "UPDATE tbl_whatsapp set stn_no = (%s) where mobile_number = '" +frm+ "' "
                        val1 =('2')
                        get_connection(update_name1,val1)
                        # print("inside stn 2 else block")
                        
                      
                print("above camp id")
                if camp_id == '1': 
                    # print("you are inside campid1")
               
                   
                    cnx = pymysql.connect (user=usr, max_allowed_packet=1073741824, password=pas, host=aws_host, database=db)
                    check_already_valid = "SELECT lang, is_lang,is_valid,is_info,id,is_verified,main_menu,sub_menu, stn_no from tbl_whatsapp where mobile_number = '" +frm+ "'"
                    print(check_already_valid)
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
                        stn_no = '0'
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
                        stn_no=str(result[8])


                    if is_verified == "0":
                        print("inside isverified 0")

                        

                        if stn_no == '1' and is_info =='0':
                            print("inside stn no1")
                            name = 'Hello 👋, Welcome to *Service Station '+ stn_no +'* 🤗  \\nTo get started, kindly enter your *Full Name* '
                            send_message(frm,name,'ask_name')  #name=  'Hello 👋, Welcome to *Vehical Service Centre!* 🤗 \\nTo get started
                            update_flag = "UPDATE tbl_whatsapp set is_info = (%s) where mobile_number = '" +frm+ "' "
                            val = ('1')
                            get_connection(update_flag,val)
                    
                        elif is_info == '1':
                            if all(x.isalpha() or x.isspace() for x in resp1):
                            
                                send_message(frm,email,'ask_email')
                                
                                update_name = "UPDATE tbl_whatsapp set is_info = (%s) where mobile_number = '" +frm+ "' "
                                val = ('00')
                                get_connection(update_name,val)
                                
                                add_data = "insert into tbl_customer(name, mobile_number) values (%s, %s)"
                                val = (resp1, frm) #need to update store id
                                get_connection(add_data,val)
                                    
                            else:
                                send_message(frm,'Please enter your *name* in the correct format.', 'invalid name')

                        
                        elif is_info == '00':
                            if (re.fullmatch(regex, resp1)):
                                send_message(frm,pincode,'pincode')
                                update_email= "UPDATE tbl_customer set email =(%s) where mobile_number = '" +frm+ "' "
                                val1 =(resp1)
                                get_connection(update_email,val1)
                                update_flag = "UPDATE tbl_whatsapp set is_info = (%s), resp1 = (%s) where mobile_number = '" +frm+ "' "
                                val = ('11','pass_email')
                                get_connection(update_flag,val)
                                # is_info = '1'

                                # resp1 = 'pass_email'
                            else:
                                send_message(frm,'Please type in your *correct email Id*','email validation')

                        elif is_info == '11':
                            if (resp1.isdigit() and len(resp1)==6):
                                send_message(frm,fprocess_complte,'Profile Completed')
                                interactive_message_with_2button(frm,"Select Option to book or cancel service ","Book_Service","Cancel_Service",'Main_Option')
                                update_pincode= "UPDATE tbl_customer set pincode =(%s) where mobile_number = '" +frm+ "' "
                                val1=(resp1)
                                get_connection(update_pincode,val1)
                                update_name = "UPDATE tbl_whatsapp set is_info = (%s) where mobile_number = '" +frm+ "' "
                                val = ('12')
                                get_connection(update_name,val)
                                # is_info = '2'
                                # is_verified = '1'
                                # print(is_verified,"isverified in last pincode")
                                # resp1 = 'pass_pincode'
                            else:
                                send_message(frm,'Please type in your *correct Pincode*','Pincode validation')

                        elif is_info=='12' and resp1== 'Book_Service':

                            print("inside is_info=='12' and resp1== 'Book_Service'")

                            update_name = "UPDATE tbl_whatsapp set is_info = (%s), is_verified = (%s) , resp1 = (%s) where mobile_number = '" +frm+ "' "
                            val = ('2','1','book_service')
                            get_connection(update_name,val)
                            is_info = '2'
                            is_verified = '1'
                            print(is_verified,"isverified in bookservice")

                        elif is_info=='12' and resp1=='Cancel_Service': 

                            print("inside is_info=='12' and resp1== 'cancel service'")

                            update_name = "UPDATE tbl_whatsapp set is_info = (%s), is_verified = (%s) , resp1 = (%s) where mobile_number = '" +frm+ "' "
                            val = ('3','2','cancel_service')
                            get_connection(update_name,val)
                            is_info = '3'
                            is_verified = '2'
                            print(is_verified,"isverified in cancel service")       

                        if stn_no == '2' and is_info =='0':
                            print("insite stn no2")
                            name = 'Hello 👋, Welcome to *Service Station '+ stn_no +'* 🤗 \\nTo get started, kindly enter your *Full Name* '
                            send_message(frm,name,'ask_name')  #name=  'Hello 👋, Welcome to *Vehical Service Centre!* 🤗 \\nTo get started
                            update_flag = "UPDATE tbl_whatsapp set is_info = (%s) where mobile_number = '" +frm+ "' "
                            val = ('A')
                            get_connection(update_flag,val)
                    
                        elif is_info == 'A':
                            if all(x.isalpha() or x.isspace() for x in resp1):
                            
                                send_message(frm,email,'ask_email')
                                update_name = "UPDATE tbl_whatsapp set is_info = (%s) where mobile_number = '" +frm+ "' "
                                val = ('AA')
                                get_connection(update_name,val)
                                add_data = "insert into tbl_customer(name, mobile_number) values (%s, %s)"
                                val = (resp1, frm) #need to update store id
                                get_connection(add_data,val)
                                    
                            else:
                                send_message(frm,'Please enter your *name* in the correct format.', 'invalid name')

                        
                        elif is_info == 'AA':
                            if (re.fullmatch(regex, resp1)):
                                send_message(frm,pincode,'pincode')
                                
                                update_email= "UPDATE tbl_customer set email =(%s) where mobile_number = '" +frm+ "' "
                                val1 =(resp1)
                                get_connection(update_email,val1)
                                update_flag = "UPDATE tbl_whatsapp set is_info = (%s), resp1 = (%s) where mobile_number = '" +frm+ "' "
                                val = ('B','pass_email')
                                get_connection(update_flag,val)
                                # resp1 = 'pass_email'
                            else:
                                send_message(frm,'Please type in your *correct email Id*','email validation')

                        elif is_info == 'B':
                            if (resp1.isdigit() and len(resp1)==6):
                                send_message(frm,fprocess_complte,'Profile Completed')
                                interactive_message_with_2button(frm,"Select Option to book or cancel service ","Book_Service","Cancel_Service",'Main_Option')
                                
                                update_pincode= "UPDATE tbl_customer set pincode =(%s) where mobile_number = '" +frm+ "' "
                                val1=(resp1)
                                get_connection(update_pincode,val1)
                                update_name = "UPDATE tbl_whatsapp set is_info = (%s) where mobile_number = '" +frm+ "' "
                                val = ('22')
                                get_connection(update_name,val)
                                is_info = '22'
                                # is_verified = '1'
                                print(is_info)

                                resp1 = 'pass_pincode'
                            else:
                                send_message(frm,'Please type in your *correct Pincode*','Pincode validation')
                    

                        elif is_info=='22' and resp1== 'Book_Service':

                            print("inside is_info=='22' and resp1== 'Book_Service'")

                            update_name = "UPDATE tbl_whatsapp set is_info = (%s), is_verified = (%s) , resp1 = (%s) where mobile_number = '" +frm+ "' "
                            val = ('2','1','book_service')
                            get_connection(update_name,val)
                            is_info = '2'
                            is_verified = '1'
                            print(is_verified,"isverified in last pincode")

                        elif is_info=='22' and resp1=='Cancel_Service': 

                            print("inside is_info=='22' and resp1== 'cancel_service'")

                            update_name = "UPDATE tbl_whatsapp set is_info = (%s), is_verified = (%s) , resp1 = (%s) where mobile_number = '" +frm+ "' "
                            val = ('3','2','cancel_service')
                            get_connection(update_name,val)
                            is_info = '3'
                            is_verified = '2'
                            print(is_verified,"isverified in last pincode")      

                        
                    if is_verified == '1' and (is_info=='2' or is_info =='22'):
                        print("inside isverified = 1 and is info 2 or 22")

                        demo_bot.eng()
                    
                    elif is_verified =='2' and is_info=='3':
                        print("inside is_verified =='2' and is_info=='3'")
                        interactive_message_with_2button(frm,"Your Booking has been canceled!! \\n To book again select option","Book_Service","STOP",'cancellation')

                        update_name = "UPDATE tbl_whatsapp set is_info = (%s),is_verified=(%s), stn_no = (%s) where mobile_number = '" +frm+ "' "
                        val = ('22','0','2')
                        get_connection(update_name,val)


            if msg_type == 'image' or msg_type == 'video' or msg_type == 'document':
                if camp_id == '1':
                    send_message(frm,'Please *enter the correct* response. ','resp1_is_other')                        
                            
                else:
                        send_message(frm,'Please *enter the correct* response. ','resp1_is_other')

            return 'Success'

        else:
            #save_message_status(response)
            return 'Success'
    except Exception as e :
        print (e)
        return 'success'

if __name__ == '__main__' :
    app.debug = False
    app.run (host='0.0.0.0', port=4000)

                

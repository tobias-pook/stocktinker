#!/bin/env python
import boto3
import os
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from dash.app import stock_cache
from dash.stock import Stock
from dash.userInfo import UserInfo
from decimal import Decimal
import numpy as np
import pandas as pd

dynamodb = boto3.resource('dynamodb')
watch_list_table = dynamodb.Table('UserWatchList')

def lambda_handler(event, context):
    watch_list = get_watch_list()
    for item in watch_list:
        print(item['user_name'] + '  ' + item['company'])
        stock = stock_cache.get(item['company'], Stock(item['company']))
        watch_list_item = {
            'projection_years': stock.n_projection_years,
            'excpected_eps': round(stock.estimated_growth * 100.,2),
            'target_yield': round(stock.target_yield * 100.,2),
            'target_p_e': round(stock.target_pe,1),
            'expected_dividends': round(stock.expected_dividends,2),
            'expected_dividends_growth': round(stock.projected_dividends_growth * 100. ,2),
            #'projected_price': projected_price,
            #'projected_total_dividends': projected_total_dividends,
            #'target_price':  target_price,
            #'current_price':  current_target_price,
            'alert_price':  round(stock.target_price,2)
            }
        try:
            userInfo = UserInfo(item['user_name'])
            if 'alert_price' in item and not pd.isna(stock.current_price) and stock.current_price < float(item['alert_price']):
                if not 'last_mail_sent' in item or datetime.utcnow()-timedelta(days=14) > datetime.fromisoformat(item['last_mail_sent']):
                    #datetime.datetime.now()-datetime.timedelta(seconds=20)
                    email = getUserEmail(userInfo, item['user_name'])
                    send_mail(email, item['company'], item['company_name'])
                    item['last_mail_sent'] = datetime.utcnow().isoformat()
            #item['target_price'] = Decimal(str(round(stock.target_price,2)))
            #item['projected_price'] = Decimal(str(round(stock.projected_price,2)))
            if not pd.isna(stock.current_price):
                item['current_price'] = Decimal(str(round(stock.current_price,2)))
            new_epsTTM = Decimal(str(round(stock.ratios["earnings-per-share-%s" % stock.currency].iloc[-1], 2 )))
            if not pd.isna(new_epsTTM) and item['epsTTM'] != new_epsTTM:
                email = getUserEmail(userInfo, item['user_name'])
                send_change_eps_mail(email, item['company'], item['company_name'], item['epsTTM'], new_epsTTM)
                item['epsTTM'] = new_epsTTM
            
            userInfo.put_company_to_watch_list(item)
        except Exception as e:
            print(item)
            print(e)
    print("TaskScheduler")
    return 200
def getUserEmail(userInfo, userName):
    settings = userInfo.get_settings()
    email = userName#item['user_name']
    if settings:
        email = settings['email']
    return email
def get_watch_list():
    response = watch_list_table.scan()
    data = response['Items']

    while 'LastEvaluatedKey' in response:
        response = watch_list_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])
    return data

def send_mail(mail_to, company, company_name):
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = os.getenv("MAIL_FROM", "alerts@3f.rocks")

    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the 
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    #CONFIGURATION_SET = "ConfigSet"

    # The subject line for the email.
    SUBJECT = "3F-Tool Alert on " + company_name

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = (company_name +" (" + company + ") has fallen below your alert price.\nIf you would like to unsubscribe edit your user settings or reply to this mail."
            )
            
    # The HTML body of the email.
    BODY_HTML = "<p>" + company_name +"(" + company + ") has fallen below your alert price.</p><p>If you would like to unsubscribe edit your user settings or reply to this mail.</p>"           

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses')

    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    mail_to,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            #ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
def send_change_eps_mail(mail_to, company, company_name, old_EPS, new_EPS):
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = os.getenv("MAIL_FROM", "alerts@3f.rocks")

    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the 
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    #CONFIGURATION_SET = "ConfigSet"

    # The subject line for the email.
    SUBJECT = "3F-Tool EPS TTM change on " + company_name

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = ("EPS TTM for" + company_name +" (" + company + ") has change from "+str(old_EPS) + " to " + str(new_EPS) +". You might adjust your target price calculation and your alert price accordingly.\nIf you would like to unsubscribe edit your user settings or reply to this mail."
            )
            
    # The HTML body of the email.
    BODY_HTML = "<p>EPS TTM for" + company_name +" (" + company + ") has change from "+str(old_EPS) + " to " + str(new_EPS) +". You might adjust your target price calculation and your alert price accordingly.</p><p>If you would like to unsubscribe edit your user settings or reply to this mail.</p>"           

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses')

    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    mail_to,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            #ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])

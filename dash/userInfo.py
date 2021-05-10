#!/bin/env python
import boto3
from boto3.dynamodb.conditions import Key
dynamodb = boto3.resource('dynamodb')
watch_list_table = dynamodb.Table('UserWatchList')
settings_table = dynamodb.Table('UserSettings')
client = boto3.client('cognito-idp')
from dash.app import app
from dash.server import access_token

class UserInfo():
    ''' Save user info"

    '''
    def __init__(self,
                 user_name):
        self.user_name = user_name

    def get_settings(self):
        response = settings_table.get_item(
            Key={
                'user_name': self.user_name
            })
        if not 'Item' in response:
            token = access_token(app.server)
            user_attr = client.get_user(
                AccessToken=token
            )['UserAttributes']
            email = next(x for x in user_attr if x["Name"] == 'email' )["Value"]
            self.put_settings({'email':email})
            return {'email': email}
        return response['Item']
    def put_settings(self, settings):
        settings['user_name'] = self.user_name
        response = settings_table.put_item(Item=settings)

    def put_company_to_watch_list(self, watch_list_item):
        watch_list_item['user_name'] = self.user_name
        response = watch_list_table.put_item(
            Item=watch_list_item
        )
        return response
    def remove_company_from_watch_list(self, company):
        response = watch_list_table.delete_item(
            Key={
                'user_name': self.user_name,
                'company': company
            }
        )
        return response
    def get_company_from_watch_list(self, company):
        response = watch_list_table.get_item(
            Key={
                'user_name': self.user_name,
                'company': company
            }
        )
        if not 'Item' in response:
            return None
        return response['Item']
    def get_watch_list(self):        
        response = watch_list_table.query(
            KeyConditionExpression=Key('user_name').eq(self.user_name)
        )
        return response['Items']

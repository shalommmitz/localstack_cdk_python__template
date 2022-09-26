import json
import boto3
import os
import re
from datetime import datetime, date, timedelta
from utils import Aws

def get_users(events):
    aws = Aws()
    users_table = aws._get_users_table()
    res_body = { "users": users_table }
    # { "isBase64Encoded": true|false, "statusCode": httpStatusCode, "headers": { "headerName": "headerValue", ... },"body": "..."}

    return {
        'isBase64Encoded': False,
        'statusCode': 200,
        'body': json.dumps( res_body )
    }

def set_user_weight(events):
    aws = Aws()
    users_table = aws._get_users_table()
    userID = events["pathParameters"]["userID"]
    weight = events["pathParameters"]["weight"]
    if userID not in users_table.keys():
        return {
            'statusCode': 404,
            "body": "Page not found"
        }
    today = datetime.utcnow().date().isoformat()  
    # item = {'UserID':{'N': userID},'UtcDate':{'S':today}, "Weight":{'N': weight}}
    item = {'UserID': int(userID),'UtcDate':today, "Weight": weight}
    res = aws._put_table_item("weights", item)

    return {
        'statusCode': 200,
        'body': json.dumps(res["ResponseMetadata"]["RetryAttempts"])
    }


def get_stats(events):
    aws = Aws()
    path = events['path']
    if path == "/MttW/fullStats":
        limit_data_to_last_3_days = False
    elif path == "/MttW/threeDaysStats":
        limit_data_to_last_3_days = True
    else:   # If there is no valid path, return no data
        print(f'ERROR: in get_stats: expected path not found. Actual path: "{path}"') 
        return False
    weights = aws._get_weights_table(limit_data_to_last_3_days)
    stats = {"weights": weights}
    return {
        'statusCode': 200,
        'body': json.dumps(stats)
    }

def events_handler(events, context):
    ######## Intialization ##########
    print("Starting events_handler")
    ######## Route according to path ##########
    #/MttW/users ['GET']
    #/MttW/user/{userID}/weight/{weight} ['POST']
    #/MttW/fullStats ['GET']
    #/MttW/threeDaysStats ['GET']
    http_method = events['httpMethod']
    path = events['path']
    valid_paths = []
    valid_paths.append( {"path": "^/MttW/users$", "method": "GET", "handler": get_users} )
    valid_paths.append( {"path": "^/MttW/user/[0-9]{1,3}/weight/[0-9]{2,3}(\.[0-9]{0,3})$", 
                         "method": "POST", "handler": set_user_weight} )
    valid_paths.append( {"path": "^/MttW/fullStats$", "method": "GET", "handler": get_stats} )
    valid_paths.append( {"path": "^/MttW/threeDaysStats$", "method": "GET", "handler": get_stats} )
    for valid_path in valid_paths:
        if re.findall( valid_path["path"], path):
            print(f'The path "{path}" matched filter "{valid_path["path"]}"')
            return valid_path["handler"](events)
    print(f'The path "{path}" did not matched any filter - will be ignored')
    return {
        'statusCode': 500,
        "body": "Unknown path"
    }

if __name__=="__main__":
    context = {}
    #events = { 'httpMethod': "POST", 'path': '/MttW/user/1/weight/22.' }
    #events["pathParameters"]  = {}
    #events["pathParameters"]["userID"] = "1"
    #events["pathParameters"]["weight"] = "22"
    #events_handler(events, context)
    #exit()
    
    events = { 'httpMethod': "GET", 'path': '/MttW/users' }
    events_handler(events, context)
    events = { 'httpMethod': "GET", 'path': '/MttW/fullStats' }
    events_handler(events, context)
    


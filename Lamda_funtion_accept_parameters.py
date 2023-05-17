import boto3
import datetime
import json

s3 = boto3.resource('s3')
bucket_name = 'chakradahars3'
key_name = 'file{}.json'

def lambda_handler(event, context):
    try:
        # Parse input data
        body = event['body']
        timestamp = str(datetime.datetime.now())
        body["timestamp"] = timestamp
        
        # Save JSON file in S3 bucket
        json_data = json.dumps(body)
        file_name = key_name.format(timestamp.replace(" ", "_"))
        s3.Object(bucket_name, file_name).put(Body=json_data)

        # Log the S3 object creation event
        print(f"Object created in S3 bucket {bucket_name}: {file_name}")

        return {
            "file_name": file_name,
            "status": "success"
        }

    except Exception as e:
        print(e)
        return {
            "status": e
        }
import json
import boto3
import csv
import os
import time
import requests
from botocore.exceptions import BotoCoreError, ClientError

# AWS clients
logs_client = boto3.client("logs")
s3_client = boto3.client("s3")
dynamodb_client = boto3.resource("dynamodb")
sqs_client = boto3.client("sqs")

# Environment Variables
S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
DYNAMODB_TABLE_NAME = os.environ["DYNAMODB_TABLE_NAME"]
API_ENDPOINT = os.environ["API_ENDPOINT"]
DLQ_URL = os.environ["DLQ_URL"]

def fetch_cloudwatch_logs(log_group, log_stream):
    """Fetch logs from CloudWatch"""
    try:
        response = logs_client.get_log_events(logGroupName=log_group, logStreamName=log_stream)
        logs = [event["message"] for event in response["events"]]
        return logs
    except (BotoCoreError, ClientError) as e:
        print(f"Error fetching logs: {e}")
        return None

def save_logs_to_csv(logs, csv_filename):
    """Save logs to a CSV file"""
    with open(csv_filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Message"])
        for log in logs:
            writer.writerow([time.time(), log])

def convert_csv_to_json(csv_filename, json_filename):
    """Convert CSV file to JSON"""
    json_data = []
    with open(csv_filename, "r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            json_data.append(row)

    with open(json_filename, "w") as json_file:
        json.dump(json_data, json_file, indent=4)

    return json_data

def upload_to_s3(json_filename):
    """Upload JSON file to S3"""
    try:
        s3_client.upload_file(json_filename, S3_BUCKET_NAME, json_filename)
        print(f"Uploaded {json_filename} to S3")
    except (BotoCoreError, ClientError) as e:
        print(f"Error uploading to S3: {e}")

def upload_to_dynamodb(json_data):
    """Upload JSON data to DynamoDB"""
    table = dynamodb_client.Table(DYNAMODB_TABLE_NAME)
    for item in json_data:
        try:
            table.put_item(Item=item)
        except (BotoCoreError, ClientError) as e:
            print(f"Error inserting into DynamoDB: {e}")

def send_to_api(json_data, retries=3):
    """Send JSON data to an API with retries"""
    for attempt in range(retries):
        try:
            response = requests.post(API_ENDPOINT, json=json_data, timeout=5)
            if response.status_code == 200:
                print("Successfully sent data to API")
                return True
            else:
                print(f"API call failed, attempt {attempt+1}: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error making API call: {e}")
        time.sleep(2)  # Backoff strategy
    
    print("Max retries reached, sending to DLQ")
    send_to_dlq(json_data)
    return False

def send_to_dlq(json_data):
    """Send failed API data to Dead Letter Queue (DLQ)"""
    try:
        sqs_client.send_message(
            QueueUrl=DLQ_URL,
            MessageBody=json.dumps(json_data)
        )
        print("Sent data to DLQ")
    except (BotoCoreError, ClientError) as e:
        print(f"Error sending to DLQ: {e}")

def lambda_handler(event, context):
    log_group = event["log_group"]
    log_stream = event["log_stream"]

    logs = fetch_cloudwatch_logs(log_group, log_stream)
    if not logs:
        return {"status": "No logs found"}

    csv_filename = "/tmp/logs.csv"
    json_filename = "/tmp/logs.json"

    save_logs_to_csv(logs, csv_filename)
    json_data = convert_csv_to_json(csv_filename, json_filename)

    upload_to_s3(json_filename)
    upload_to_dynamodb(json_data)
    
    send_to_api(json_data)

    # Clean up files
    os.remove(csv_filename)
    os.remove(json_filename)

    return {"status": "Process completed"}

import boto3
from django.conf import settings
from botocore.exceptions import ClientError

def get_lock_table():
    
    dynamodb = boto3.resource(
        "dynamodb",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    return dynamodb.Table(settings.AWS_DYNAMODB_TABLE_NAME)

def create_dynamodb_lock(file_hash):
    lock_table = get_lock_table()
    try:
        lock_table.put_item(
            Item={'file_hash': file_hash},
            ConditionExpression='attribute_not_exists(file_hash)'
        )
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return False
        raise

def delete_dynamodb_lock(file_hash):
    lock_table = get_lock_table()
    lock_table.delete_item(Key={'file_hash': file_hash})

def dynamodb_lock_exists(file_hash):
    lock_table = get_lock_table()
    
    print("AWS Region: ", settings.AWS_REGION)
    print("S3 bucket name: ", settings.AWS_STORAGE_BUCKET_NAME)
    print("Lock table name: ", settings.AWS_DYNAMODB_TABLE_NAME)

    response = lock_table.get_item(Key={'file_hash': file_hash})
    return 'Item' in response

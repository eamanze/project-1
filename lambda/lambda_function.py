import os, json, boto3, base64, requests
from urllib.parse import unquote_plus
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

CF_KEY_PAIR_ID = os.environ['CF_KEY_PAIR_ID']
CF_CDN_DOMAIN = os.environ['CF_CDN_DOMAIN']
CALLBACK_URL = os.environ['DJANGO_CALLBACK_URL']
secret_name = "lambda/cdn/private_key2"
region_name = "us-east-2"
secrets_client = boto3.client("secretsmanager", region_name=region_name)
secret_value = secrets_client.get_secret_value(SecretId=secret_name)
#PRIVATE_KEY_PEM = json.loads(secret_value["SecretString"])["CF_PRIVATE_KEY_PEM"]
PRIVATE_KEY_PEM = secret_value["SecretString"]

def generate_signed_url(url, expire_minutes):
    expire_time = int((datetime.utcnow() + timedelta(minutes=expire_minutes)).timestamp())
    policy_dict = {
        "Statement": [
            {
                "Resource": url,
                "Condition": {
                    "DateLessThan": {
                        "AWS:EpochTime": expire_time
                    }
                }
            }
        ]
    }
    policy = json.dumps(policy_dict)

    private_key = serialization.load_pem_private_key(
        PRIVATE_KEY_PEM.encode(), password=None, backend=default_backend()
    )
    signature = private_key.sign(policy.encode(), padding.PKCS1v15(), hashes.SHA1())
    encoded_signature = base64.b64encode(signature).decode().replace('+','-').replace('=','_').replace('/','~')

    signed_url = f"{url}?Expires={expire_time}&Signature={encoded_signature}&Key-Pair-Id={CF_KEY_PAIR_ID}"
    return signed_url

def lambda_handler(event, context):
    for record in event.get('Records', []):
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        s3_uri = f"s3://{bucket}/{key}"
        file_hash = key.split('/')[-1].replace('.pdf', '')
        cloudfront_url = f"https://{CF_CDN_DOMAIN}/{key}"

        signed_url = generate_signed_url(cloudfront_url, expire_minutes=30)

        payload = {
            "file_hash": file_hash,
            "s3_uri": s3_uri,
            "cdn_url": signed_url
        }

        print("📤 Posting to Django:", CALLBACK_URL)
        res = requests.post(CALLBACK_URL, json=payload)
        print(f"✅ Status: {res.status_code}, Response: {res.text}")

    return {"status": "done"}
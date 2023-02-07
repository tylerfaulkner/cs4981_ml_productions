#This script loads all the logs from minio and counts the number of ham and spam emails.
import json
import boto3
import io

#Connect to Minio
target = boto3.resource('s3',
    endpoint_url='http://127.0.0.1:9000',
    aws_access_key_id="minioadmin",
    aws_secret_access_key="minioadmin",
    aws_session_token=None,
    config=boto3.session.Config(signature_version='s3v4'),
    verify=False
)
client = boto3.client('s3',
    endpoint_url="http://127.0.0.1:9000",
    aws_access_key_id="minioadmin",
    aws_secret_access_key="minioadmin",
    aws_session_token=None,
    config=boto3.session.Config(signature_version='s3v4'),
    verify=False
)

#Load all json files from the log-files bucket
bucket = target.Bucket('log-files')
ham_count = 0
spam_count = 0
for obj in bucket.objects.all():
    if obj.key.endswith('.json'):
        bytes_buffer = io.BytesIO()
        client.download_fileobj('log-files', obj.key, bytes_buffer)
        byte_value = bytes_buffer.getvalue()
        str_values = byte_value.decode().split('\n')
        for email in str_values:
            if len(email) > 0:
                email = json.loads(email)
                if email['event'] == 'classify::email::post':
                    if email['predicted_class'] == 'ham':
                        ham_count += 1
                    else:
                        spam_count += 1
print('Ham count: ', ham_count)
print('Spam count: ', spam_count)
print('Total count: ', ham_count + spam_count)

print('Ham percentage: ', ham_count / (ham_count + spam_count))
print('Spam percentage: ', spam_count / (ham_count + spam_count))
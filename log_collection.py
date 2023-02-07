from pygtail import Pygtail
import boto3
import os
import datetime
import sys
import time

if __name__ == "__main__":
    n = len(sys.argv)
    if n != 2:
        print('There can only be one argument of the collection wait period in minutes')
        exit()
    while True:
        start = time.time()
        reader = Pygtail('log_file.json')
        #print(lines)
        target = boto3.resource('s3',
            endpoint_url="http://127.0.0.1:9000",
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin",
            aws_session_token=None,
            config=boto3.session.Config(signature_version='s3v4'),
            verify=False
        )
        lines = reader.read()
        current_time = datetime.datetime.now()
        date = str(current_time.year)[2:4] + str(current_time.month) + str(current_time.day)
        time_str = str(current_time.hour) + str(current_time.minute) + str(current_time.second)
        filename = 'log_file_' + date + '-' + time_str + '.json'
        bucket = target.Bucket("log-files")
        if lines is not None:
            print('Uploading to MinIO')
            bucket.put_object(Key=filename, Body=lines)
        print('Done! Will check agin in', sys.argv[1], 'minutes.')
        end=time.time()
        sleep_time = int(sys.argv[1])*60 - (end - start)
        time.sleep(sleep_time)

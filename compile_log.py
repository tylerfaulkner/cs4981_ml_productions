#Compile all the json objects into a dataframe then save the data frame to a parquet file in Minio
import pandas as pd
import json
import io
import boto3

def load_logs_from_minio():
    # Connect to Minio
    print("Connecting to Minio")
    target = boto3.resource('s3',
        endpoint_url="http://127.0.0.1:9000",
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

    #Load the all the object
    bucket = target.Bucket('log-files')
    #load all the objects in the bucket
    rows = []
    print("Loading the log files")
    for obj in bucket.objects.all():
        #Convert the json file into a json object
        #The json file ocnsists of 
        key = obj.key
        if "json" in key:
            obj = obj.get()
            bytes_buffer = io.BytesIO()
            client.download_fileobj('log-files', key, bytes_buffer)   
            byte_value = bytes_buffer.getvalue()
            bytes_buffer.close()
            str_values = byte_value.decode().split('\n')
            i=0
            while i < len(str_values):
                str_v = str_values[i]
                if len(str_v) > 0: #Last line is empty
                    rows.append(json.loads(str_v))
                i+=1
    #convert the list of json objects into a dataframe
    df = pd.DataFrame(rows)
    print("Dataframe shape: ", df.shape)
    print(df.head())
    #Save the dataframe to a parquet file in Minio using boto3
    df.to_parquet('temp.parquet')
    client.put_object(Bucket='log-files', Key='log.parquet', Body=open('temp.parquet', 'rb'))
    #par_buffer.close()

if __name__ == "__main__":
    load_logs_from_minio()
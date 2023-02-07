#Offline Model Development
import json
import pickle
import io
import datetime
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import boto3
from sklearn.feature_extraction.text import CountVectorizer

def load_logs_from_minio():
        # Connect to Minio
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

    #Load the bucket training-data using the boto3 library
    bucket = target.Bucket('training-data')
    #load all the objects in the bucket
    rows = []
    for obj in bucket.objects.all():
        #Convert the json file into a json object
        #The json file ocnsists of 
        key = obj.key
        if "json" in key:
            obj = obj.get()
            bytes_buffer = io.BytesIO()
            client.download_fileobj('training-data', key, bytes_buffer)   
            byte_value = bytes_buffer.getvalue()
            str_values = byte_value.decode().split('\n')
            i=0
            while i < len(str_values):
                str_v = str_values[i]
                if len(str_v) > 0: #Last line is empty
                    rows.append(json.loads(str_v))
                i+=1
    return rows



def train_new_model():
    """
    Train a new model using the saved results json
    Save the new model to Minio using pickle
    """
    params = json.load(open('experiment_results.json'))

    rows = load_logs_from_minio()
    df = pd.DataFrame(rows)
    df = df.set_index('email_id')
    print(df.head())

    #Split the data into training and testing
    X = df['body'].to_numpy()
    y = df['label'].to_numpy()

    #Convert the labels to 0 and 1
    y[y == 'spam'] = 1
    y[y == 'ham'] = 0
    y = y.astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    #Balance the classes in the training data
    #This is done by undersampling the majority class
    minority_class_indices = np.where(y_train == 0)[0]
    #Get the indices of the majority class
    majority_class_indices = np.where(y_train == 1)[0]
    #Downsample the majority class
    majority_class_indices_downsampled = np.random.choice(majority_class_indices, len(minority_class_indices), replace=False)
    
    #Combine the majority and minority class indices
    downsampled_indices = np.concatenate([minority_class_indices, majority_class_indices_downsampled])
    #Downsample the training data
    X_train = X_train[downsampled_indices]
    y_train = y_train[downsampled_indices]

    #Use CountVectorizer to convert the text into a matrix of token counts
    #This will be used to train the model
    vectorizer = CountVectorizer(min_df=params['parameters']['min_df'])
    X_train = vectorizer.fit_transform(X_train)
    X_test = vectorizer.transform(X_test)

    #Train the model
    model = LinearRegression()
    model.fit(X_train, y_train)

    #Connect to Minio
    target = boto3.resource('s3',
        endpoint_url="http://127.0.0.1:9000",
        aws_access_key_id="minioadmin",
        aws_secret_access_key="minioadmin",
        aws_session_token=None,
        config=boto3.session.Config(signature_version='s3v4'),
        verify=False
    )
    bucket = target.Bucket('models')

    #Put necessary data into a dictionary to be saved using pickle
    data = {
        #'model': model,
        #'vectorizer': vectorizer,
        'parameters': params['parameters'],
        #'input': X_train,
        'class_balance': 'undersampled'
    }
    #Get current datetime
    now = datetime.datetime.now()
    dt_string = now.strftime("(%d_%m_%Y)_(%H_%M_%S)")

    file_name = 'model_' + dt_string + '.pkl'
    #Save the model to Minio
    with open(file_name, 'wb') as f:
        pickle.dump(data, f)
        pickle.dump(model, f)
        pickle.dump(vectorizer, f)
        
        bucket.upload_file(file_name, file_name)

if __name__ == '__main__':
    train_new_model()




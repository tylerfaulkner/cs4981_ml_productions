#Email prediction service API
import structlog
from flask import Flask, request
import pickle
import boto3
import io
import json
import numpy as np


app = Flask(__name__)

#Global variables for models
model = None
vectorizer = None

def load_models():
    #Load the most recent model from Minio
    #Connect to Minio
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
    bucket = target.Bucket('models')
    most_recent_model_name = None
    most_recent_model_date = None
    #Get the most recent model
    for obj in bucket.objects.all():
        if obj.key.startswith('model_'):
            model_file = obj.key
            if most_recent_model_date == None:
                most_recent_model_date = obj.last_modified
                most_recent_model_name = model_file
            else:
                if obj.last_modified > most_recent_model_date:
                    most_recent_model_date = obj.last_modified
                    most_recent_model_name = model_file
    if most_recent_model_name is not None:
        print("Loading model: " + most_recent_model_name)
        #Load the model
        obj = obj.get()
        with open('temp.pkl', 'wb') as f:
            client.download_fileobj('models', most_recent_model_name, f)
        #client.download_fileobj('models', model_file, bytes_buffer)
        #data = target.Bucket("models").Object(model_file).get()['Body'].read()
        global model
        global vectorizer
        with open('temp.pkl', 'rb') as f:
            pickle.load(f)
            model = pickle.load(f)
            vectorizer = pickle.load(f)





@app.route('/classify')
def classify_email():
    """
    Takes a JSON object as payload.  The object contains the key “email” with the value being another 
    object.  The email object should have the key “body” with the value being a String.  The request 
    should return another JSON object with the key “predicted_class” and a value of “spam” or “ham.”
    """

    #Get the email body
    email_body = request.json['email']['body']
    #Transform the email body
    #print('Vecotrizing email body')
    email_vec = vectorizer.transform([email_body])

    #print(email_vec.shape)

    #Predict the class
    #print('Predicting class')
    pred_prob = model.predict(email_vec)[0]

    predicted_class = 'ham'
    if pred_prob > 0.9:
        predicted_class = 'spam'

    print(predicted_class)

    #Log the event
    #print('Logging event')
    logger = structlog.get_logger()
    logger.info(event="classify::email::post", predicted_class=predicted_class)

    #Return the predicted class
    return {'predicted_class': predicted_class}



# main driver function
if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.

    with open("log_file.json", "at", encoding="utf-8") as log_fl:
        structlog.configure(
            processors=[structlog.processors.TimeStamper(fmt="iso"),
                        structlog.processors.JSONRenderer()],
            logger_factory=structlog.WriteLoggerFactory(file=log_fl))
        load_models()
        app.run(debug=True, port=8888, threaded=True)

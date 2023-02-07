#Email prediction service API
import structlog
from flask import Flask, request
import pickle
import boto3
import io


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
    #Get the most recent model
    for obj in bucket.objects.all():
        if obj.key.startswith('model_'):
            model_file = obj.key
            #Load the model
            obj = obj.get()
            bytes_buffer = io.BytesIO()
            client.download_fileobj('models', model_file, bytes_buffer)
            byte_value = bytes_buffer.getvalue()
            model_config = pickle.loads(byte_value)
            global model
            model = model_config['model']
            global vectorizer
            vectorizer = model_config['vectorizer']





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
    email_body = vectorizer.transform(email_body)
    #Predict the class
    predicted_class = model.predict(email_body)

    #Log the event
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
        app.run(debug=True, port=8888)

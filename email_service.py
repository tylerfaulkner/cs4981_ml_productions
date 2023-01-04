import json
import psycopg2
import os
import random

from flask import Flask, jsonify, request
import time
import datetime
import structlog

app = Flask(__name__)

VALID_LABELS=['read', 'spam', 'important']


def get_db_connection():
    # figure out how to not have the environment variables showing
    conn = psycopg2.connect(host=os.environ['POSTGRES_HOST'],
                            database=os.environ['POSTGRES_DATABASE'],
                            user= os.getenv('POSTGRES_USERNAME'),
                            password=os.getenv('POSTGRES_PASSWORD'))
    return conn

# get connection to the database
conn = get_db_connection()

# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    return 'Hello World'


@app.route('/email', methods=['POST'])
def receive_emails():
    print("test")
    cur = conn.cursor()
    print('Printing JSON...')
    #Content-type:application/json expected
    email_data = request.json
    print(email_data)
    cur.execute('INSERT INTO emails (received_timestamp, email_object)'
                'VALUES (%s, %s) RETURNING email_id',
                (datetime.datetime.now(), json.dumps(email_data)))
    id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    return jsonify({"email_id": id})

@app.route('/mailbox/email/<int:email_id>', methods=['GET'])
# returns json object with the key "email" and associated value of a String
def get_email(email_id):
    logger = structlog.get_logger()
    logger.info(event="email::id::body::get",
        email_id=email_id)
    cur = conn.cursor()
    #a %s can be used in an execute to insert a string
    cur.execute('SELECT email_object FROM emails WHERE email_id=%s', str(email_id))
    email = cur.fetchone()[0]
    cur.close()
    return jsonify({'email':email})

@app.route('/mailbox/email/<int:email_id>/folder', methods=['GET'])
# get the folder containing the email
def get_folder(email_id):
    cur = conn.cursor()
    #a %s can be used in an execute to insert a string
    cur.execute('SELECT folder FROM emails WHERE email_id=%s', str(email_id))
    folder = cur.fetchone()[0] #items from select are returned in a list
    cur.close()
    return folder

@app.route('/mailbox/email/<int:email_id>/labels', methods=['GET'])
# returns json object with the fields "email_id" and "labels"
def get_labels(email_id):
    logger = structlog.get_logger()
    logger.info(event="email::id::labels::get",
        email_id=email_id)
    cur = conn.cursor()
    #a %s can be used in an execute to insert a string
    cur.execute('SELECT labels FROM emails WHERE email_id=%s', str(email_id))
    labels = cur.fetchone()[0] #items from select are returned in a list
    cur.close()
    return labels

@app.route('/mailbox/folder/<string:folder>', methods=['GET'])
# list emails in a given folder
def emails_in_folder():
    return "jfda"

@app.route('/mailbox/labels/<string:label>', methods=['GET'])
# list emails with given label
def emails_with_label():
    return "kleraho"

@app.route('/mailbox/email/<int:email_id>/folder/<string:folder>', methods=['POST'])
# moves email to the given folder
def move_email(email_id, folder):
    logger = structlog.get_logger()
    logger.info(event="email::id::folder::post",
        email_id=email_id,
        folder=folder)
    return "gkdsl"

@app.route('/mailbox/email/<int:email_id>/label/<string:label>', methods=['PUT'])
# mark the given email with the given label
def mark_email(email_id, label):
    logger = structlog.get_logger()
    logger.info(event="email::id::label::put",
        email_id=email_id,
        label=label)
    global VALID_LABELS
    if label not in VALID_LABELS:
        return 'Invalid Label, must be read, important, or spam'
    cur = conn.cursor()
    #get current labels
    cur.execute('SELECT labels FROM emails where email_id=%s', str(email_id))
    labels = cur.fetchone()[0]
    print(labels)
    #add new label
    labels.append(label)
    #psycopg2 can only convert list types, so convert back
    cur.execute('UPDATE emails SET labels=%s WHERE email_id=%s', (list(set(labels)), str(email_id)))
    #Commit all changes
    conn.commit()
    cur.close()
    return 'Success'

@app.route('/mailbox/email/<int:email_id>/label/<string:label>', methods=['DELETE'])
def delete_label():
    return "fjdkl"


# main driver function
if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.

    with open("log_file.json", "at", encoding="utf-8") as log_fl:
        structlog.configure(
            processors=[structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer()],
                logger_factory=structlog.WriteLoggerFactory(file=log_fl))
        app.run(debug=True,port=8888)
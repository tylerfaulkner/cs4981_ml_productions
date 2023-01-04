import json
import psycopg2
import os
import random

from flask import Flask, jsonify, request
import datetime
import structlog

app = Flask(__name__)

VALID_LABELS=['read', 'spam', 'important']
VALID_FOLDERS = ['Inbox', 'Archive', 'Trash', 'Important']


def get_db_connection():
    # figure out how to not have the environment variables showing
    conn = psycopg2.connect(host=os.environ['POSTGRES_HOST'],
                            database=os.environ['POSTGRES_DATABASE'],
                            user= os.getenv('POSTGRES_USERNAME'),
                            password=os.getenv('POSTGRES_PASSWORD'))
    return conn

# get connection to the database
conn = get_db_connection()

@app.route('/mailbox/email/<int:email_id>', methods=['GET'])
# returns json object with the key "email" and associated value of a String
def get_email(email_id):
    logger = structlog.get_logger()
    logger.info(event="email::id::body::get",
        email_id=email_id)
    cur = conn.cursor()
    #a %s can be used in an execute to insert a string
    cur.execute('SELECT email_object FROM emails WHERE email_id=%s', (str(email_id),))
    email = cur.fetchone()[0]
    cur.close()
    return jsonify({'email':email})

@app.route('/mailbox/email/<int:email_id>/folder', methods=['GET'])
# get the folder containing the email
def get_folder(email_id):
    logger = structlog.get_logger()
    logger.info(event="email::id::folder::get",
                email_id=email_id)
    cur = conn.cursor()
    #a %s can be used in an execute to insert a string
    cur.execute('SELECT folder FROM emails WHERE email_id=%s', (str(email_id),))
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
    cur.execute('SELECT labels FROM emails WHERE email_id=%s', (str(email_id),))
    labels = cur.fetchone()[0] #items from select are returned in a list
    cur.close()
    return labels

def get_first_element(element):
    return element[0]

@app.route('/mailbox/folder/<string:folder>', methods=['GET'])
# list emails in a given folder
def emails_in_folder(folder):
    logger = structlog.get_logger()
    logger.info(event="folder::get", folder=folder)
    global VALID_FOLDERS
    if folder not in VALID_FOLDERS:
        return 'Invalid Folder, must be inbox, archive, trash or sent'
    cur = conn.cursor()
    print(folder)
    cur.execute('SELECT email_id FROM emails WHERE folder=\''+ str(folder)+'\';')
    raw_data = cur.fetchall()
    cur.close()
    print(raw_data[0][0])
    emails = list(map(get_first_element, raw_data))
    print(emails)
    return emails

@app.route('/mailbox/label/<string:label>', methods=['GET'])
# list emails with given label
def emails_with_label(label):
    logger = structlog.get_logger()
    logger.info(event="label::get", label=label)
    global VALID_LABELS
    if label not in VALID_LABELS:
        return 'Invalid Label, must be read, important, or spam'
    cur = conn.cursor()
    cur.execute('SELECT email_id FROM emails WHERE \''+ str(label) +'\' = ANY(labels);')
    raw_data = cur.fetchall()
    cur.close()
    emails = list(map(get_first_element, raw_data))
    return emails

@app.route('/mailbox/email/<int:email_id>/folder/<string:folder>', methods=['PUT'])
# moves email to the given folder
def move_email(email_id, folder):
    logger = structlog.get_logger()
    global VALID_FOLDERS
    if folder not in VALID_FOLDERS:
        return 'Invalid Folder, must be inbox, archive, trash or sent'
    logger.info(event="email::id::folder::post",
        email_id=email_id,
        folder=folder)
    cur = conn.cursor()
    cur.execute('UPDATE emails SET folder=%s WHERE email_id=%s', (str(folder), str(email_id)))
    cur.close()
    return 'Success'

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
    cur.execute('SELECT labels FROM emails where email_id=%s', (str(email_id),))
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
def delete_label(email_id, label):
    logger = structlog.get_logger()
    logger.info(event="email::id::label::delete", email_id=email_id, label=label)
    global VALID_LABELS
    if label not in VALID_LABELS:
        return 'Invalid Label, must be read, important, or spam'
    cur = conn.cursor()
    # get current labels
    cur.execute('SELECT labels FROM emails where email_id=%s', (str(email_id),))
    labels = cur.fetchone()[0]
    print(labels)
    # remove label
    if label in labels:
        labels.remove(label)
    cur.execute('UPDATE emails SET labels=%s WHERE email_id=%s', (list(set(labels)), str(email_id)))
    # Commit all changes
    conn.commit()
    cur.close()
    return 'Success'


# main driver function
if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.

    with open("log_file.json", "at", encoding="utf-8") as log_fl:
        structlog.configure(
            processors=[structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer()],
                logger_factory=structlog.WriteLoggerFactory(file=log_fl))
        app.run(debug=True,port=8889)
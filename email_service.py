import json
import psycopg2
import os
import random

from flask import Flask, jsonify, request
import time
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

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
    email_data = request.data.decode('utf-8')
    print(email_data)
    email_data = json.loads(email_data)
    email_object = {
        "to": email_data['to'],
        "from": email_data['from'],
        "subject": email_data['subject'],
        "body": email_data['body']
    }
    cur.execute('INSERT INTO emails (received_timestamp, email_object)'
                'VALUES (%s, %s)',
                (time.time(), json.dumps(email_object)))
    conn.commit()
    cur.close()
    return jsonify({"email_id": random.randint(1, 1000)})

@app.route('/mailbox/email/<int:email_id>', methods=['GET'])
# returns json object with the key "email" and associated value of a String
def get_email(email_id):
    #not sure if this is right at all:/
    print(email_id)
    cur = conn.cursor()
    cur.execute('SELECT email_id, email_object FROM emails WHERE email_id=email_id')  # I have no idea how to put a variable into this statement
    emails = cur.fetchall()
    print(emails)
    cur.close()
    return emails

@app.route('/mailbox/email/<int:email_id>/folder', methods=['GET'])
# get the folder containing the email
def get_folder():
    return "yo"

@app.route('/mailbox/email/<int:email_id>/labels', methods=['GET'])
# returns json object with the fields "email_id" and "labels"
def get_labels():
    return "hehe"

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
def move_email():
    return "gkdsl"

@app.route('/mailbox/email/<int:email_id>/label/<string:label>', methods=['PUT'])
# mark the given email with the given label
def mark_email():
    return "hkfdla"

@app.route('/mailbox/email/<int:email_id>/label/<string:label>', methods=['DELETE'])
def delete_label():
    return "fjdkl"


# main driver function
if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    app.run(debug=True,port=8888)
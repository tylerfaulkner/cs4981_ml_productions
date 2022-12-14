import json
import uuid
from flask import Flask, jsonify

app = Flask(__name__)


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
    #ensure format is correct? & then create ran
    return jsonify({'email_id': uuid.uuid4()})

@app.route('/mailbox/email<email_id:int>', methods=['GET'])
def get_email():
    return "hi"

@app.route('/mailbox/email/<email_id:int>/folder', methods=['GET'])
def get_folder():
    return "yo"

@app.route('/mailbox/email/<email_id:int>/labels', methods=['GET'])
def get_labels():
    return "hehe"

@app.route('/mailbox/folder/<folder:str>', methods=['GET'])
def emails_in_folder():
    return "heahkl"

@app.route('/mailbox/labels/<label:str>', methods=['GET'])
def emails_with_label():
    return "kleraho"

@app.route('/mailbox/email/<email_id:int>/folder/<folder:str>', methods=['POST'])
def move_email():
    return "gkdsl"

@app.route('/mailbox/email/<email_id:int>/label/<label:str>', methods=['PUT'])
def mark_email():
    return "hkfdla"

@app.route('/mailbox/email/<email_id:int>/label/<label:str>', methods=['DELETE'])
def delete_label():
    return "fjdkl"


# main driver function
if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    app.run(debug=True,port=8888)
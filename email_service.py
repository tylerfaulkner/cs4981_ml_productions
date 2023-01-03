import json
import uuid
import random
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
    return jsonify({'email_id': random.randint(1, 1000)})

@app.route('/mailbox/email/<int:email_id>', methods=['GET'])
def get_email():
    return "hi"

@app.route('/mailbox/email/<int:email_id>/folder', methods=['GET'])
def get_folder():
    return "yo"

@app.route('/mailbox/email/<int:email_id>/labels', methods=['GET'])
def get_labels():
    return "hehe"

@app.route('/mailbox/folder/<string:folder>', methods=['GET'])
def emails_in_folder():
    return "heahkl"

@app.route('/mailbox/labels/<string:label>', methods=['GET'])
def emails_with_label():
    return "kleraho"

@app.route('/mailbox/email/<int:email_id>/folder/<string:folder>', methods=['POST'])
def move_email():
    return "gkdsl"

@app.route('/mailbox/email/<int:email_id>/label/<string:label>', methods=['PUT'])
def mark_email():
    return "hkfdla"

@app.route('/mailbox/email/<int:email_id>/label/<string:label>', methods=['DELETE'])
def delete_label():
    return "fjdkl"


# main driver function
if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    app.run(debug=True,port=5000)
import json
import psycopg2
import os
from flask import Flask, jsonify, request
import datetime
import structlog

app = Flask(__name__)

def get_db_connection():
    # figure out how to not have the environment variables showing
    conn = psycopg2.connect(host=os.environ['POSTGRES_HOST'],
                            database=os.environ['POSTGRES_DATABASE'],
                            user= os.getenv('POSTGRES_USERNAME'),
                            password=os.getenv('POSTGRES_PASSWORD'))
    return conn

# get connection to the database
conn = get_db_connection()


@app.route('/email', methods=['POST'])
def receive_emails():
    logger = structlog.get_logger()
    logger.info(event="email::post")
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
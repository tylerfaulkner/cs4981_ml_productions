import structlog
from flask import Flask

app = Flask(__name__)


@app.route('/classify_email', methods=['POST'])
def classify_email(email_object):
    logger = structlog.get_logger()
    logger.info(event="classify::email::post")
    return ""


# main driver function
if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.

    with open("log_file.json", "at", encoding="utf-8") as log_fl:
        structlog.configure(
            processors=[structlog.processors.TimeStamper(fmt="iso"),
                        structlog.processors.JSONRenderer()],
            logger_factory=structlog.WriteLoggerFactory(file=log_fl))
        app.run(debug=True, port=8888)

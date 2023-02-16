:: Start all the email services and  minio
start C:\minio\minio.exe server C:\minio\data
start cmd /k python email_service.py
start cmd /k python log_collection.py 1
start cmd /k python mailbox_service.py
start cmd /k python prediction_service.py
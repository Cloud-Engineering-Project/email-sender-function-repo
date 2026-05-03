import base64
import json
import os
import smtplib
from email.message import EmailMessage

from google.cloud import storage

GMAIL_ADDRESS = os.environ["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]

storage_client = storage.Client()


def email_sender(event, context):
    message_data = base64.b64decode(event["data"]).decode("utf-8")
    payload = json.loads(message_data)

    user_email = payload["email"]
    bucket_name = payload["bucket"]
    object_name = payload["object"]
    output_filename = payload["output_filename"]
    content_type = payload["content_type"]

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(object_name)

    converted_base64 = blob.download_as_text()
    converted_bytes = base64.b64decode(converted_base64)

    email = EmailMessage()
    email["From"] = GMAIL_ADDRESS
    email["To"] = user_email
    email["Subject"] = "Your converted file is ready"

    email.set_content("Your converted file is attached.")

    maintype, subtype = content_type.split("/", 1)

    email.add_attachment(
        converted_bytes,
        maintype=maintype,
        subtype=subtype,
        filename=output_filename,
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        smtp.send_message(email)

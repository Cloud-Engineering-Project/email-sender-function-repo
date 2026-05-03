import base64
import json
import os

from google.cloud import storage
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]
FROM_EMAIL = os.environ["FROM_EMAIL"]

storage_client = storage.Client()


def email_sender(event, context):
    message_data = base64.b64decode(event["data"]).decode("utf-8")
    payload = json.loads(message_data)

    email = payload["email"]
    bucket_name = payload["bucket"]
    object_name = payload["object"]
    output_filename = payload["output_filename"]
    content_type = payload["content_type"]

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(object_name)

    converted_base64 = blob.download_as_text()

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=email,
        subject="Your converted file is ready",
        plain_text_content="Your converted file is attached.",
    )

    attachment = Attachment(
        FileContent(converted_base64),
        FileName(output_filename),
        FileType(content_type),
        Disposition("attachment"),
    )

    message.attachment = attachment

    sg = SendGridAPIClient(SENDGRID_API_KEY)
    sg.send(message)
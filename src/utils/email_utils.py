# src/utils/email_utils.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.logging_utils import setup_logger

logger = setup_logger()

def load_email_config():
    # Hardcoded email configuration for testing
    email_config = {
        'server': 'smtp01.stackpole.ca',
        'from': 'tyler.careless@johnsonelectric.com',
        'to': ['tyler.careless@johnsonelectric.com'],
        'subject': 'Daily Temperature Sensor Report'
    }
    return email_config

def get_email_list():
    # Hardcoded email list for testing
    email_list = ['tyler.careless@johnsonelectric.com']
    return email_list

def send_email(report, email_config):
    message = MIMEMultipart("alternative")
    message["Subject"] = email_config['subject']
    message["From"] = email_config['from']
    message["To"] = ", ".join(get_email_list())  # Use the dynamic list
    msg_body = MIMEText(report, "html")
    message.attach(msg_body)
    
    # Try to connect to the SMTP server and send the email.
    server = None
    try:
        server = smtplib.SMTP(email_config['server'])
        server.sendmail(email_config['from'], get_email_list(), message.as_string())
        logger.info("Email sent successfully to {}".format(email_config['to']))
    except smtplib.SMTPException as e:
        logger.error(f"Failed to send email: {e}")
        raise Exception("Failed to send email due to SMTP issue.") from e
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise Exception("An unexpected error occurred when sending an email.") from e
    finally:
        if server:
            server.quit()

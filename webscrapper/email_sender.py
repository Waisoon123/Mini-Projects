# Description: This script sends an email with the daily cyber news summary to the specified email address.

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
from dotenv import load_dotenv
import os


def send_email(df):
    # Convert the DataFrame to an HTML table
    html = df.to_html()

    # Set up the email
    msg = MIMEMultipart()
    msg['Subject'] = 'Your Daily Cyber News Summary'
    msg['From'] = os.getenv('EMAIL_FROM')
    msg['To'] = os.getenv('EMAIL_TO')
    msg.attach(MIMEText(html, 'html'))

    # Send the email
    try:
        with smtplib.SMTP('smtp.gmail.com', 465) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(os.getenv('SMTP_LOGIN'), os.getenv('SMTP_PASSWORD'))
            smtp.send_message(msg)
            print('Email sent successfully')
    except Exception as e:
        print(f'Error sending email: {e}')

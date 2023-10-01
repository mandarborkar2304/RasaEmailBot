import re

from rasa_sdk import Tracker, Action
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Text


class SendEmailAction(Action):

    def name(self) -> Text:
        return "action_send_email"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict) -> List[Dict[Text, Any]]:

        email_intent = tracker.latest_message['intent'].get('name')

        if email_intent == 'send_email':
            # Extract the email address from user message
            user_message = tracker.latest_message['text']
            to_email = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', user_message)

            if to_email:
                to_email = to_email.group()
                subject = "DataXL Solutions Test Email"
                message = "This is the demo email fro testing purpose"

                # Send the email
                response = send_email(subject, message, to_email)

                # Set email_status slot based on the response
                if response == "Mail Sent":
                    dispatcher.utter_message("Mail Sent")
                    return [SlotSet("email_status", "success")]
                else:
                    dispatcher.utter_message("Sorry, an error occurred while sending the email.")
                    return [SlotSet("email_status", "failure")]
            else:
                dispatcher.utter_message("Sorry, I couldn't find a valid email address in your message.")
                return [SlotSet("email_status", "failure")]
        return []


def send_email(subject, message, to_email):
    # Your Gmail account credentials
    email_address = 'your email id'
    email_password = 'your password'

    # Create an SMTP client session
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_address, email_password)
    except Exception as e:
        return str(e)

    # Compose the email
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    # Send the email
    try:
        server.sendmail(email_address, to_email, msg.as_string())
        server.quit()
        return "Mail Sent"
    except Exception as e:
        return str(e)

from twilio.rest import Client
from flask import current_app
import random

code_storage = {}  # Temporary storage for development

def send_verification_code(phone_number, username):
    code = str(random.randint(100000, 999999))
    code_storage[username] = code

    client = Client(current_app.config['TWILIO_ACCOUNT_SID'], current_app.config['TWILIO_AUTH_TOKEN'])
    message = client.messages.create(
        body=f"Your verification code is {code}",
        from_=current_app.config['TWILIO_PHONE_NUMBER'],
        to=phone_number
    )
    return message.sid

def get_stored_code(username):
    return code_storage.get(username)

def clear_stored_code(username):
    code_storage.pop(username, None)

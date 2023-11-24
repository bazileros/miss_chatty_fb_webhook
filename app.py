from flask import Flask, request
import json
import requests
import os
from dotenv import load_dotenv
import logging

app = Flask(__name__)
GRAPH_API_URL = None
VERIFY_TOKEN = None

# Load environment variables


def configure():
    load_dotenv()
    global GRAPH_API_URL, VERIFY_TOKEN
    GRAPH_API_URL = f'https://graph.facebook.com/v18/me/messages?access_token={os.getenv("PAGE_ACCESS_TOKEN")}'
    VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# Get the Graph API URL


def get_graph_api_url():
    return GRAPH_API_URL

# Call the Send API to send a response to the user


def call_send_api(sender_psid, response):
    payload = {
        'recipient': {'id': sender_psid},
        'message': response,
        'messaging_type': 'RESPONSE'
    }
    headers = {'content-type': 'application/json'}
    try:
        r = requests.post(get_graph_api_url(), json=payload, headers=headers)
        r.raise_for_status()
        logging.info(r.text)
    except requests.exceptions.RequestException as e:
        logging.error(f"Error occurred during API call: {e}")

# Handle incoming messages


def handle_message(sender_psid, received_message):
    if "text" in received_message:
        response = {"text": f'You just sent me: {received_message["text"]}'}
        call_send_api(sender_psid, response)
    else:
        response = {"text": "This chatbot only accepts text messages"}
        call_send_api(sender_psid, response)

# Home route


@app.route('/', methods=['GET', 'POST'])
def home():
    return 'HOME'

# Webhook route


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            logging.info('WEBHOOK VERIFIED')
            return request.args.get("hub.challenge"), 200
        else:
            return 'ERROR', 403
    if request.method == 'POST':
        data = request.get_json()
        if 'object' in data and data['object'] == 'page':
            entries = data['entry']
            for entry in entries:
                webhook_event = entry['messaging'][0]
                sender_psid = webhook_event['sender']['id']
                logging.info('Sender PSID: {}'.format(sender_psid))
                if 'message' in webhook_event:
                    handle_message(sender_psid, webhook_event['message'])
            return 'EVENT_RECEIVED', 200
        else:
            return 'ERROR', 400


if __name__ == '__main__':
    configure()
    logging.basicConfig(level=logging.INFO)

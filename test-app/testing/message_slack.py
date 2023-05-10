from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
import sys
import common


def message_slack_channel(api_token, channel, message):
    client = WebClient(api_token)

    try:
        print(f'Sending ${message} to ${channel}')
        client.chat_postMessage(channel=channel, text=message)
        print("Message sent")
    except SlackApiError as e:
        print(f'Error sending message: ${e}')
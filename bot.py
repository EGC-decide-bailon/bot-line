from __future__ import unicode_literals
import os
import sys
from argparse import ArgumentParser
from flask import Flask, request, Response, abort
from linebot import (LineBotApi, WebhookParser)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,)

app = Flask(__name__)

# VARIABLES TOKEN PARA LA CONEXION CON LINE
# channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
# channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)


##PARA EL DESPLIEGUE EN LOCAL

channel_secret = '8a401267ff13adf83d61a8d3634f27fb'
channel_access_token = 'SPmbgV2uPoHOOs1cGwS+lSfUdkluJ2vMXCzgzqQZBovOVgKfupIeYpD7WmRdYwdd+GB+VK3MqN5Pi2cWDCKMu2iMVJ8oi1ptq7TNeJCsDI2JTeNYNiSO1l0DQiVe6Dzq455FUJJnpywlxusspxlfDwdB04t89/1O/w1cDnyilFU='

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    #app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        
        msg = event.message.text

        if(msg=='commands_list'):
            commands_list(event)
        elif(msg=='login'):
            login_decide(event)
        elif(msg=='info_votaciones'):
            get_votaciones(event)
        elif(msg=='info_votacion'):
            get_votacion(event)
        elif(msg=='votar'):
           vote(event)
        else:
            not_command(event)

        #line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))

    return 'OK'


def commands_list(event):
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Lista completa de comandos:\n\nlogin: inicia sesión en Decide\n\ninfo_votaciones: obtén información de todas las votaciones' + 
        ' disponibles en este momento\n\ninfo_votacion: obtén información detallada sobre una votación\n\nvotar: participa en una votación'))
def login_decide(event):
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=''))
def get_votaciones(event):
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=''))
def get_votacion(event):
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=''))
def vote(event):
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=''))
def not_command(event):
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Perdona pero no he renocido el comando. Si quieres ver la lista completa de comandos prueba a escribir "commands_list"'))


if __name__ == "__main__":
    app.run(debug=True)
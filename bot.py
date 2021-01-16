from __future__ import unicode_literals
import os
import sys
import json
import requests
from argparse import ArgumentParser
from flask import Flask, request, Response, abort
from linebot import (LineBotApi, WebhookParser)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,)

app = Flask(__name__)

# VARIABLES TOKEN PARA LA CONEXION CON LINE
# channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
# channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
URL_BASE = 'https://decide-voting.herokuapp.com/'

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

DIC = {}

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
        
        msg = event.message.text.split()

        if(msg[0][0]=='/'):

            if(msg[0]=='/commands_list'):
                commands_list(event)
            elif(msg[0]=='/login'):
                login_decide(event)
            elif(msg[0]=='/info_votaciones'):
                get_votaciones(event)
            elif(msg[0]=='/info_votacion'):
                get_votacion(event)
            elif(msg[0]=='/votar'):
                vote(event)
        else:
            not_command(event)

    return 'OK'


def commands_list(event):
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Lista completa de comandos:\n\n/login: inicia sesión en Decide escribiendo tus credenciales con el siguiente formato:\n'
        'login [user] [pass]\n\n/info_votaciones: obtén información de todas las votaciones disponibles en este momento' + 
        '\n\n/info_votacion: obtén información detallada sobre una votación\n\n/votar: participa en una votación con el siguiente formato:\nvotar [número de la votación] [si/no]'))

def login_decide(event):
    #recuperamos las credenciales del mensaje del usuario
    msg = event.message.text.split()
    user = msg[1]
    password = msg[2]

    #preparamos la peticion a Decide
    url = URL_BASE + "authentication/login/"
    auth = {
        "username": str(user),
        "password": str(password)
    }

    response = requests.post(url,auth)
    data = response.json()
    token = data["token"]

    if(response.status_code==200):
        DIC[str(event.source.user_id)] = token
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Has iniciado sesión con éxito.\nSi quieres ver información sobre las votaciones prueba a escribir\n"/info_votaciones"'))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Parece que ha habido un error. Revisa tus credenciales.'))

def get_votaciones(event):
    
    #recuperamos el token del usuario para mostrar solo las votaciones en la que puede participar
    try:
        token = DIC[str(event.source.user_id)]
        headers = {"token": str(token)}
        url = URL_BASE + "voting/"
        response = requests.get(url, headers = headers)
        data = response.json()
    
        #parseamos las votaciones para poder mostrarlas en un mensaje
        votaciones = parseVotaciones(data)

        cadena = ''

        for v in votaciones:
            cadena = cadena + 'ID: ' + str(v.get("id")) + '\n' + 'Nombre: ' + str(v.get("name")) + '\n' + 'Descripción: ' + str(v.get("desc"))+ '\n' + 'Pregunta: ' + str(v.get("question").get("desc")) + '\n\n'

    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Parece que ha habido un error. ¿Has iniciado sesión?'))

    if(response.status_code==200):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Esta es la lista de votaciones en las que puedes participar:\n\n' + cadena + 'Para obtener información sobre una' +
            ' votacion en concreto prueba el comando\n"/info_votacion" seguido del id de la votación que deseas mostrar'))
            

def get_votacion(event):
    try:
        token = DIC[str(event.source.user_id)]
        headers = {"token": str(token)}
        url = URL_BASE + "voting/"
        response = requests.get(url, headers = headers)
        data = response.json()

        votaciones = parseVotaciones(data)
        msg = event.message.text.split()
        idVotacion = msg[1]
        votacion = votaciones[int(idVotacion)-1]
        cadena = 'ID: ' + str(votacion.get("id")) + '\nNombre: ' + str(votacion.get("name")) + '\nDescripción: ' + str(votacion.get("desc"))+ '\nPregunta: ' + str(votacion.get("question").get("desc")) + '\nOpciones: ' + str(votacion.get("question").get("options")[0].get("option")) + ' / ' + str(votacion.get("question").get("options")[1].get("option"))
    
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Parece que ha habido un error. Comprueba el id introducido e inténtalo de nuevo'))

    if(response.status_code==200):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Aquí esta la información sobre la votación solicitada:\n\n' + cadena + '\n\nSi deseas participar en esta votación' +
            ' utiliza el comando "/votar seguido del id de la votación y tu respuesta.\n\nEjemplo: quiero votar sí a la votacion 1.\n/votar 1 si'))

def vote(event):
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=''))

def not_command(event):
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Perdona pero no he renocido el comando.\nSi quieres ver la lista completa de comandos prueba a escribir "/commands_list"'))

def parseVotaciones(votaciones):

    res = []
    for vot in votaciones:
        v = {'id': vot['id'], 'name': vot['name'], 'desc': vot['desc'], 'end_date': vot['end_date'],
             'start_date': vot['start_date'], 'question': vot['question'], 'pub_key': vot['pub_key']}

        if v['start_date'] is not None and v['end_date'] is None:
            res.append(v)

    return res

if __name__ == "__main__":
    app.run(debug=True)
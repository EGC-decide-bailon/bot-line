import unittest
import requests
import json
import sys
import bot

URL_BASE = "https://decide-voting.herokuapp.com/"
user = "user"
password = "rinoceronte2"

DIC = {}

class TestMethods(unittest.TestCase):

    #Test login con credenciales válidas
    def test_login_exito(self):
        url = URL_BASE + "authentication/login/"
        auth = {"username": str(user),
                "password": str(password)}
        response = requests.post(url, auth)
        data = response.json()
        token = data["token"]
        DIC[str(user)] = token

        self.assertEqual(response.status_code, 200)

    #Test login con credenciales inválidas
    def test_login_error(self):
        url = URL_BASE + "authentication/login/"
        auth = {"username": "pepe",
                 "password":"123"}
        response = requests.post(url, auth)

        self.assertEqual(response.status_code, 400)

    #Test obtener votaciones
    def test_retrieve_votaciones_exito(self):
        token = DIC[str(user)]
        headers = {"token": str(token)}
        url = URL_BASE + "voting/"
        response = requests.get(url, headers = headers)

        self.assertEqual(response.status_code, 200)

    #Test obtener una votación a partir de su ID con ID válido
    def test_retrieve_votacion_exito(self):
        token = DIC[str(user)]
        headers = {"token": str(token)}
        url = URL_BASE + "voting/"
        response = requests.get(url, headers = headers)

        #Definimos un mensaje similar al que enviaría el cliente
        mensaje = "/info_votacion 1"

        #seleccionamos una única votación
        data = response.json()
        votaciones = bot.parseVotaciones(data)
        msg = mensaje.split()
        idVotacion = msg[1]
        votacion = votaciones[int(idVotacion)-1]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(votacion.get("ID"),1)

    #Test obtener una votación a partir de su ID con un ID que no existe
    def test_retrieve_votacion_error(self):
        token = DIC[str(user)]
        headers = {"token": str(token)}
        url = URL_BASE + "voting/"
        response = requests.get(url, headers = headers)

        #Definimos un mensaje similar al que enviaría el cliente
        mensaje = "/info_votacion 9"

        #seleccionamos una única votación
        data = response.json()
        votaciones = bot.parseVotaciones(data)
        msg = mensaje.split()
        idVotacion = msg[1]
        votacion = votaciones[int(idVotacion)-1]

        self.assertEqual(response.status_code, 200)
        self.assertoken = DIC[str(user)]
        headers = {"token": str(token)}
        url = URL_BASE + "voting/"
        response = requests.get(url, headers = headers)

        #Definimos un mensaje similar al que enviaría el cliente
        mensaje = "/info_votacion 1"

        #seleccionamos una única votación
        data = response.json()
        votaciones = bot.parseVotaciones(data)
        msg = mensaje.split()
        idVotacion = msg[1]
        votacion = votaciones[int(idVotacion)-1]
        print(votacion)

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(votacion)



if __name__ == '__main__':
    unittest.main()
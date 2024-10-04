import pyttsx3
import speech_recognition as sr
import datetime
import logging
from tuya_iot import TuyaOpenAPI, TUYA_LOGGER, AuthType

# Opciones de voz / idioma
id1 = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_DAVID_11.0"
id2 = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0"
id3 = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_ES-ES_HELENA_11.0"

# Configuración del SDK de Tuya
ACCESS_ID = 'ngm5k9cayftydve9hejr'
ACCESS_KEY = '4f4b3787c3454b7499fd7bc4a69e3a2e'
USERNAME = 'sofii.ruiz24@gmail.com'
PASSWORD = 'Necochea247'
# ASSET_ID = '150990207'
DEVICE_ID = '650a71abca16f29455x4od'
# ENDPOINT = "https://openapi-ueaz.tuyaus.com"

# ACCESS_ID = "tu-access-id"
# ACCESS_KEY = "tu-access-key"
# USERNAME = "tu-username"
# PASSWORD = "tu-password"
# DEVICE_ID = "tu-device-id"

# Inicializar el cliente de Tuya


def inicializar_tuya():

    api = TuyaOpenAPI("https://openapi-ueaz.tuyaus.com",
                      ACCESS_ID, ACCESS_KEY, AuthType.CUSTOM)

    # Autenticación mediante el SDK, se genera el token automáticamente
    api.connect(USERNAME, PASSWORD)  # Conexión usando credenciales
    TUYA_LOGGER.setLevel(logging.DEBUG)
    return api

# Encender luz


def encender_luz(api):
    command = {'commands': [{'code': 'switch_led', 'value': True}]}
    api.post(f'/v1.0/iot-03/devices/{DEVICE_ID}/commands', command)
    hablar("He encendido la luz.")

# Apagar luz


def apagar_luz(api):
    command = {'commands': [{'code': 'switch_led', 'value': False}]}
    api.post(f'/v1.0/iot-03/devices/{DEVICE_ID}/commands', command)
    hablar("He apagado la luz.")

# Ajustar brillo


def ajustar_brillo(api, nivel):
    command = {'commands': [{'code': 'brightness', 'value': nivel}]}
    api.post(f'/v1.0/iot-03/devices/{DEVICE_ID}/commands', command)
    hablar(f"He ajustado el brillo a {nivel} por ciento.")

# Función para que el asistente pueda ser escuchado


def hablar(mensaje):
    engine = pyttsx3.init()
    engine.setProperty("voice", id3)  # Usa la voz en español
    engine.say(mensaje)
    engine.runAndWait()

# Escuchar y convertir audio a texto


def transformar_audio_texto():
    r = sr.Recognizer()
    with sr.Microphone() as origen:
        r.pause_threshold = 0.8
        print("Ya puedes hablar")
        audio = r.listen(origen)
        try:
            pedido = r.recognize_google(audio, language="es-ES")
            print(f"Dijiste: {pedido}")
            return pedido.lower()
        except:
            print("No entendí el audio")
            return "sigo esperando"

# Función saludo inicial


def saludo_inicial():
    hora = datetime.datetime.now()
    if hora.hour < 6 or hora.hour > 20:
        momento = "Buenas noches"
    elif 6 <= hora.hour < 13:
        momento = "Buen día"
    else:
        momento = "Buenas tardes"
    hablar(f"{momento}, ¿en qué te puedo ayudar?")

# Función central del asistente


def centro_pedido():
    api = inicializar_tuya()  # Inicializar la API de Tuya
    saludo_inicial()
    comenzar = True
    while comenzar:
        pedido = transformar_audio_texto()

        if "encender luz" in pedido:
            encender_luz(api)
        elif "apagar luz" in pedido:
            apagar_luz(api)
        elif "ajustar brillo" in pedido:
            try:
                # Extraer el nivel de brillo del pedido
                nivel = int([s for s in pedido.split() if s.isdigit()][0])
                ajustar_brillo(api, nivel)
            except (IndexError, ValueError):
                hablar("No entendí el nivel de brillo. Por favor, repite el comando.")
        elif "adiós" in pedido:
            hablar("Nos vemos, avísame si necesitas otra cosa.")
            break


# Ejecutar el asistente
centro_pedido()

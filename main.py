import pyttsx3
import speech_recognition as sr
import datetime
import logging
import time
import requests
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

# Colores
colores_basicos = {
    "rojo": (0, 1000, 1000),      # Hue=0, Saturation=1000, Value=1000
    "azul": (240, 1000, 1000),    # Hue=240, Saturation=1000, Value=1000
    "amarillo": (60, 1000, 1000),  # Hue=60, Saturation=1000, Value=1000
    "verde": (120, 1000, 1000),   # Hue=120, Saturation=1000, Value=1000
    "violeta": (280, 1000, 1000),  # Hue=280, Saturation=1000, Value=1000
    "naranja": (30, 1000, 1000),  # Hue=30, Saturation=1000, Value=1000
    "blanco": (0, 0, 1000),       # Hue=0, Saturation=0, Value=1000
}


# Inicializar el cliente de Tuya
def inicializar_tuya():

    api = TuyaOpenAPI("https://openapi-ueaz.tuyaus.com",
                      ACCESS_ID, ACCESS_KEY, AuthType.CUSTOM)

    # Autenticación mediante el SDK, se genera el token automáticamente
    api.connect(USERNAME, PASSWORD)  # Conexión usando credenciales
    TUYA_LOGGER.setLevel(logging.DEBUG)
    return api

# Funcion Encender luz


def encender_luz(api):
    command = {'commands': [{'code': 'switch_led', 'value': True}]}
    api.post(f'/v1.0/iot-03/devices/{DEVICE_ID}/commands', command)
    hablar("He encendido la luz.")

# Funcion Apagar luz


def apagar_luz(api):
    command = {'commands': [{'code': 'switch_led', 'value': False}]}
    api.post(f'/v1.0/iot-03/devices/{DEVICE_ID}/commands', command)
    hablar("He apagado la luz.")

# Funcion Ajustar brillo


def ajustar_brillo(api, nivel):
    if 10 <= nivel <= 1000:
        command = {'commands': [{'code': 'bright_value_v2', 'value': nivel}]}
        api.post(f'/v1.0/iot-03/devices/{DEVICE_ID}/commands', command)
    else:
        hablar("El valor del brillo debe estar entre 10 y 1000.")


def extraer_nivel_brillo(pedido):
    # Convertimos el pedido en una lista de palabras
    palabras = pedido.split()

    # Buscamos la posición de la palabra "brillo"
    if "brillo" in palabras:
        # Tomamos todas las palabras después de "brillo"
        posicion_brillo = palabras.index("brillo")
        # Retornamos las palabras después de "brillo"
        return " ".join(palabras[posicion_brillo + 1:])
    else:
        return None  # Si no encuentra la palabra "brillo"

# Funcion cambiar de color


def cambiar_color(api, h, s, v):
    if 0 <= h <= 360 and 0 <= s <= 1000 and 0 <= v <= 1000:
        command = {
            'commands': [{
                'code': 'colour_data_v2',
                'value': {'h': h, 's': s, 'v': v}
            }]
        }
        api.post(f'/v1.0/iot-03/devices/{DEVICE_ID}/commands', command)
    else:
        print("Valores fuera de rango: h [0-360], s y v [0-1000].")


def extraer_color_basico(pedido):
    # Convertimos el pedido en una lista de palabras
    palabras = pedido.split()

    # Buscamos si alguna de las palabras es un color básico
    for palabra in palabras:
        if palabra in colores_basicos:
            return colores_basicos[palabra]  # Retornamos los valores h, s, v
    return None  # Si no se encuentra ningún color

# Funcion cuenta regresiva


def cuenta_regresiva(api, segundos):
    if 0 <= segundos <= 86400:
        command = {'commands': [{'code': 'countdown_1', 'value': segundos}]}
        api.post(f'/v1.0/iot-03/devices/{DEVICE_ID}/commands', command)
    else:
        print("El tiempo de cuenta regresiva debe estar entre 0 y 86400 segundos.")


def extraer_horas(pedido):
    # Convertimos el pedido en una lista de palabras
    palabras = pedido.split()

    # Buscamos la palabra "horas" y obtenemos la palabra anterior
    if "horas" in palabras:
        posicion_horas = palabras.index("horas")
        try:
            # Tomamos la palabra anterior a "horas" y la convertimos a número
            horas = int(palabras[posicion_horas - 1])
            return horas
        except (ValueError, IndexError):
            return None  # Si no puede convertir o si no hay número antes de "horas"
    else:
        return None  # Si no encuentra la palabra "horas"

# Funcion cambiar temperatura


def ajustar_temperatura(api, temp):
    if 0 <= temp <= 1000:
        command = {'commands': [{'code': 'temp_value_v2', 'value': temp}]}
        api.post(f'/v1.0/iot-03/devices/{DEVICE_ID}/commands', command)
    else:
        print("La temperatura debe estar entre 0 y 1000.")


def extraer_ciudad(pedido):
    # Convertimos el pedido en una lista de palabras
    palabras = pedido.split()

    # Unimos todas las palabras después de "ciudad de"
    if "ciudad" in palabras and "de" in palabras:
        # Aseguramos que "ciudad de" están juntas
        try:
            # Tomamos lo que sigue después de "ciudad de"
            posicion_ciudad_de = palabras.index("ciudad") + 2
            # Tomamos todas las palabras restantes
            ciudad = " ".join(palabras[posicion_ciudad_de:])
            return ciudad
        except IndexError:
            return None  # En caso de que no haya palabras después de "ciudad de"
    return None  # Si no encuentra "ciudad de" en el pedido


def obtener_temperatura(ciudad):
    # Open-Meteo usa latitud y longitud, necesitamos convertir la ciudad
    geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={
        ciudad}"

    try:
        # Obtener las coordenadas de la ciudad
        geo_response = requests.get(geocoding_url)
        geo_data = geo_response.json()
        lat = geo_data['results'][0]['latitude']
        lon = geo_data['results'][0]['longitude']

        # Obtener la temperatura actual
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={
            lat}&longitude={lon}&current_weather=true"
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()

        # La temperatura está en "current_weather"
        temperatura = weather_data['current_weather']['temperature']
        return temperatura
    except:
        return None  # En caso de que no se pueda obtener la temperatura


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

        if "enumerar comandos disponibles" in pedido:
            hablar("Actualmente los comandos disponibles son:")
            time.sleep(1)  # pausa
            hablar("1 encender luz")
            time.sleep(1)  # pausa
            hablar("2 apagar luz")
            time.sleep(1)  # pausa
            hablar("3 ajustar brillo (nivel de 10 a 1000)")
            time.sleep(1)  # pausa
            hablar("4 cambiar color a (colores basicos)")
            time.sleep(1)  # pausa
            hablar("5 apagar luz dentro de (horas)")
            time.sleep(1)  # pausa
            hablar("6 cambiar la temperatura")
        elif "encender luz" in pedido:
            encender_luz(api)
        elif "apagar luz" in pedido:
            apagar_luz(api)
        elif "ajustar brillo" in pedido:
            # Extraemos lo que viene después de la palabra "brillo"
            nivel_brillo_texto = extraer_nivel_brillo(pedido)
            if nivel_brillo_texto:
                try:
                    # Intentamos convertir lo extraído a un número
                    nivel = int(nivel_brillo_texto)
                    ajustar_brillo(api, nivel)
                except ValueError:
                    hablar(
                        "No entendí el nivel de brillo. Por favor, repite el comando.")
            else:
                hablar(
                    "No mencionaste el nivel de brillo. Por favor, repite el comando.")
        elif "cambiar color" in pedido:
            # Extraemos los valores del color básico
            valores_color = extraer_color_basico(pedido)
            if valores_color:
                h, s, v = valores_color  # Desempaquetamos los valores h, s, v
                cambiar_color(api, h, s, v)
            else:
                hablar(
                    "No entendí el color. Por favor, repite el comando con un color básico como rojo, azul, o verde.")
        elif "apagar luz dentro de" in pedido:
            # Extraemos el número de horas antes de la palabra "horas"
            horas = extraer_horas(pedido)
            if horas is not None:
                segundos = horas * 3600  # Convertimos horas a segundos
                cuenta_regresiva(api, segundos)
                hablar(f"Apagaré la luz en {horas} horas.")
            else:
                hablar(
                    "No entendí la cantidad de horas. Por favor, repite el comando.")
        elif "temperatura" in pedido and "ciudad de" in pedido:
            # Extraemos la ciudad del pedido
            ciudad = extraer_ciudad(pedido)
            if ciudad:
                # Obtenemos la temperatura para esa ciudad
                temperatura = obtener_temperatura(ciudad)
                if temperatura is not None:
                    hablar(f"La temperatura en {ciudad} será de {
                           temperatura} grados mañana.")
                    # Cambiamos el color según la temperatura
                    if temperatura < 20:
                        cambiar_color(api, 0, 0, 1000)  # Blanco
                        hablar("Hará frío, he puesto el color blanco.")
                    else:
                        cambiar_color(api, 30, 1000, 1000)  # Naranja
                        hablar("Hará calor, he puesto el color naranja.")
                else:
                    hablar(
                        "No pude obtener la temperatura para esa ciudad. Por favor, verifica el nombre.")
            else:
                hablar("No mencionaste una ciudad válida.")

        elif "adiós" in pedido:
            hablar("Nos vemos, avísame si necesitas otra cosa.")
            break


# Ejecutar el asistente
centro_pedido()

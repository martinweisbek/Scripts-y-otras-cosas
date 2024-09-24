import requests
from datetime import datetime
from dateutil import parser
from threading import Thread
import pandas as pd
import os, sys
import telebot
import asyncio

'''
Este Script manda por telegram avisos cada vez que hay nuevas ofertas de trabajo en abc.gob.ar
El link de la query tiene filtros configurados, luego el script filtra por distrito
'''

#Telegram info
TOKEN = "your token here"
bot = telebot.TeleBot(TOKEN) #Creo la instancia de bot

chatID = "chat_id"

# URL del formulario de login
# query_url = "https://servicios3.abc.gob.ar/valoracion.docente/api/apd.oferta.encabezado/select?rows=100000&facet=true&facet.limit=-1&facet.mincount=1&json.nl=map&facet.field=estado&fq=estado%3Apublicada&q=*:*&wt=json"
query_url = "https://servicios3.abc.gob.ar/valoracion.docente/api/apd.oferta.encabezado/select?rows=100000&facet=true&facet.limit=-1&facet.mincount=1&json.nl=map&facet.field=estado&fq=cargo%3A%22ingles%20(igs)%22&fq=estado%3Apublicada&q=*:*&"


# Lista para almacenar los IDs de ofertas procesadas hoy
listaID_hoy = []
#listaDistritos = ["GENERAL RODRIGUEZ", "MERCEDES", "PILAR", "LUJAN", "SAN  ANDRES DE GILES"]
listaDistritos = ["GENERAL RODRIGUEZ"]

try: 
    path = sys._MEIPASS
except: 
    path = os.path.abspath('.')

csv_path = os.path.join(path, "ListadoEscuelas.csv")



#============== COMANDOS TELEGRAM =============#
@bot.message_handler(commands=['start'])
def mensaje_bienvenida(message):
    bot.reply_to(message, "Hola! Soy un bot que avisa de nuevas ofertas de trabajo del ABC")


#============== FIN COMANDOS TELEGRAM =============#



def BuscarNombreEscuela(pathCsv: str, ClaveProvincia: str):
    nombreEscuela = ""
    try:
        # Leer el archivo CSV
        df = pd.read_csv(pathCsv, encoding='Windows-1252', sep=';')
        
        # Buscar la fila que coincide con la clave provincial
        resultado = df.loc[df['Clave Provincial'] == ClaveProvincia]
        
        # Si existe la clave, obtener el nombre de la escuela
        if not resultado.empty:
            nombreEscuela = resultado.iloc[0]['Nombre']
        else:
            print(f"Clave provincial {ClaveProvincia} no encontrada.")
            nombreEscuela = ""
            
    except Exception as e:
        print(f"Error: {e}")
        nombreEscuela = ""
        
    return nombreEscuela

def ObtenerDatos():
    try:
        # Realizar la solicitud GET
        response = requests.get(query_url)
        response.encoding = 'Windows-1252'
        docs = None
        if response.status_code == 200:
            print("Request exitoso!")
            data_json = response.json()
            # Extraer documentos
            docs = data_json.get('response', {}).get('docs', [])
        else:
            print(f"Error en la solicitud: {response.status_code}")
    except Exception as e:
        print("Error en 'obtenerDatos'}\n Error:", e)
        
    return docs

def FiltrarOfertas(ofertas, listadoDistritos : list):
    try:
        listaOfertas = []
    # Iterar sobre los documentos y extraer información
        for doc in ofertas:
            fechaAviso = doc.get("iniciooferta")
            distrito = doc.get("descdistrito")

            # Convertir la fecha del aviso
            date_time_obj = parser.isoparse(fechaAviso)
            fechaAviso = date_time_obj.strftime("%d/%m/%Y")
            fechaHoy = datetime.today().strftime("%d/%m/%Y")

            # if (fechaAviso == fechaHoy) and (distrito in listaDistritos):
            if (distrito in listadoDistritos):
                listaOfertas.append(doc)
        
        return listaOfertas
    except Exception as e:
        print(f"Error en 'FiltrarOfertas'\n Error: {e}")
        return None

def mensajeDiarioInformativo(ofertasFiltradas : list):
    try:
        if(ofertasFiltradas != None):
            texto_totalofertas = "*CANTIDAD DE OFERTAS HOY: " + str(len(ofertasFiltradas)) + "*"
            bot.send_message(chatID, texto_totalofertas)
    except Exception as e:
        print(f"Error'mensajeDiarioInformativo'\n Error: {e}")

def mensajeOfertaNueva(ofertasFiltradas : list) -> str:
    try:
        texto_msg = ""
        # Procesar las nuevas ofertas
        for d in ofertasFiltradas:
            id_oferta = d.get("id")
            texto = (
                "Escuela: " + str(BuscarNombreEscuela(csv_path, str(d.get("escuela", "")))) + "\n" +
                "Distrito: " + str(d.get("descdistrito", "")) + "\n" +
                "Modalidad: " + str(d.get("descnivelmodalidad", "")) + "\n" +
                "Cargo: " + str(d.get("cargo", "")) + "\n" +
                "Ubicación: " + str(d.get("domiciliodesempeno", "")) + "\n" +
                "Descripción: " + str(d.get("descripcioncargo", "")) + "\n" +
                "Curso: " + str(d.get("cursodivision", "")) + "\n" +
                "Horarios\n" +
                "  -Lunes:    " + str(d.get("lunes", "")) + "\n" +
                "  -Martes:    " + str(d.get("martes", "")) + "\n" +
                "  -Miércoles:    " + str(d.get("miercoles", "")) + "\n" +
                "  -Jueves:    " + str(d.get("jueves", "")) + "\n" +
                "  -Viernes:    " + str(d.get("viernes", "")) + "\n" +
                "  -Sábados:    " + str(d.get("sabado", "")) + "\n" +
                "==============================\n"
            )

            #Si la oferta de trabajo es nueva, no se va a encontrar en la listaID
            #Por lo que la envio por mensaje
            if id_oferta not in listaID_hoy:
                texto_msg = texto + texto_msg
                listaID_hoy.append(id_oferta) 
        
        return texto_msg
    except Exception as e:
        print(f"Error en funcoin 'MensajeOfertaNueva'\n Error: {e}")
        return ""

def iniciar_bot_polling():
    bot.polling(none_stop=True)



async def BucleOfertasNuevas():
    try:
        print("Iniciando Script...")
        #Mensaje informativo
        docs = ObtenerDatos()
        if (docs != None):
            mensajeDiarioInformativo(FiltrarOfertas(docs,listaDistritos))
    except Exception as e:
        print("Error")


    # Bucle infinito
    while True:

        try:
            mensajeDiarioEnviado = False
            texto_msg = ""
            #Obtengo los datos en formato JSON
            docs = ObtenerDatos()

            #Filtro las ofertas que me sirven
            ofertasFiltradas = FiltrarOfertas(docs,listaDistritos)

            #Corroboro la hora actual para mandar un mensaje a las 8 am
            
            HoraActual = datetime.today().hour
            if(HoraActual == 8 and mensajeDiarioEnviado == False):
                mensajeDiarioInformativo(ofertasFiltradas)
                mensajeDiarioEnviado = True

            elif (HoraActual != 8 and mensajeDiarioEnviado == True):
                mensajeDiarioEnviado = False
            
            #Si hay una oferta nueva genero un mensaje
            texto_msg = mensajeOfertaNueva(ofertasFiltradas)
            

            #Si el texto no es vacio, envio un mensaje por whatsapp
            if (texto_msg != ""):
                # Enviar el mensaje solo si hay nuevas ofertas
                print(texto_msg)
                bot.send_message(chatID, texto_msg)

            # Pausa para evitar sobrecargar la CPU y hacer solicitudes excesivas
            await asyncio.sleep(900)  # Esperar 5 minutos antes de la siguiente iteración
        except Exception as e:
            print(f"Error {e}")
            await asyncio.sleep(120)  # Esperar 5 minutos antes de la siguiente iteración






if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.create_task(BucleOfertasNuevas())

    # Ejecuta el bot en un hilo separado
    bot_thread = Thread(target=iniciar_bot_polling)
    bot_thread.start()

    # Ejecuta el bucle de eventos de asyncio
    loop.run_forever()
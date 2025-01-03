import datetime
import os
import uuid
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from joblib import load
from DataModel import DataModel

from transformers import BertTokenizer
import re
import unicodedata
import torch
import pandas as pd

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer
from io import BytesIO

# ---------------------------------
# Preparación del modelo y CORS
# ---------------------------------

app = FastAPI()
model = load("assets/trained_bert_model.joblib")

data = pd.read_excel('assets/Datos de entrenamiento.xlsx')
labels = data['Intención'].tolist()
label_mapping = list(set(labels))  # Nombres de las clases del conjunto de datos de entrenamiento

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------
# Endpoints Auxiliares
# ---------------------------------

@app.get("/")
def read_root():
   return {"Hello": "World"}

@app.get("/integrantes")
def intgrantes():
   return "Juan Ignacio Arbelaez Velez, Brenda Catalina Barahona Pinilla y Juan Diego Gonzalez Gomez"

# ---------------------------------
# Variables
# ---------------------------------

var_tipoConsulta = ""

# Consulta Persona
var_tipoDocumento = ""
var_numeroDocumento = ""

# Consulta Vehículo
var_procedencia = "Nacional" # Por defecto
var_consultarPor = ""
var_numeroPlaca = ""
var_numeroVIN = ""
var_numeroSOAT = ""
var_aseguradora = ""
var_numeroRTM = ""

var_finalizo_consulta = False

# ---------------------------------
# Hilo principal
# ---------------------------------

@app.post("/talk")
def talk(input: DataModel):
  global var_finalizo_consulta

  texto = limpiar_datos(input.texto)

  identificar_datos(texto)

  if not var_finalizo_consulta:
    if var_tipoConsulta == "":
      return make_predictions(texto)
    
    elif var_tipoConsulta == "Consulta Persona":
      return consulta_persona()
    
    elif var_tipoConsulta == "Consulta Vehículo":
      return consulta_vehiculo()
  else:
    respondio_si = re.search(r"\bsi\b", texto, re.IGNORECASE)
    respondio_no = re.search(r"\bno\b", texto, re.IGNORECASE)

    if respondio_si and (not respondio_no):
      read_root()
      return ("¿Con qué más te puedo ayudar?")
    elif respondio_no and (not respondio_si):
      return ("Esperamos haberte ayudado. ¡Que tengas un excelente día!")
    else:
      return("No entendí tu respuesta, ¿podrías repetirla? Si/No")

# ---------------------------------
# Método para limpiar los datos
# ---------------------------------
def limpiar_datos(texto):
  texto = unicodedata.normalize('NFD', texto)
  texto = texto.encode('ascii', 'ignore').decode('utf-8')
  texto = texto.lower()
  texto = re.sub(r'[^a-z0-9\s]', '', texto)
  return texto

# ---------------------------------
# Método para predecir la intención
# ---------------------------------
bolsa_persona = [
  "licencia", "conduccion", "multa", "infraccion", "multas", "infracciones", "certificados medicos", "comparendos", "comparendo"
]
bolsa_vehiculo = [
  "soat"
]
bolsa_stopwords = [
  "quiero", "consultar", "consulta", "averiguar", "preguntar", "pregunta", "solicitar", "verificar", "verifico", "acerca", "sobre",
  "que", "cual", "cuales", "donde", "quien", "quienes", "cuantas", "cuantos", "como", "saber", "hacer",
  "obtener", "obtengo", "recuperar", "recupero", "tramitar", "tramito"
]

def make_predictions(texto):
    global var_tipoConsulta

    # Tokenizar los textos de entrada para hacer la predicción
    if (len(texto.split(" ")) <3):
      return("¿Qué consulta te gustaría realizar?")

    # Limpieza
    def contiene_palabras(texto, lista_palabras):
        for palabra in lista_palabras:
            if palabra.lower() in texto.lower():
                return True
        return False

    # Verificar si el texto contiene palabras de alguna lista
    contiene_persona = contiene_palabras(texto, bolsa_persona)
    contiene_vehiculo = contiene_palabras(texto, bolsa_vehiculo)

    if contiene_persona and not contiene_vehiculo:
      var_tipoConsulta = "Consulta Persona"
      return consulta_persona()

    elif contiene_vehiculo and not contiene_persona:
      var_tipoConsulta = "Consulta Vehículo"
      return consulta_vehiculo()

    else:
      # Limpieza StopWords
      def remover_stopwords(texto, stopwords):
          palabras = texto.split()
          palabras_filtradas = [palabra for palabra in palabras if palabra.lower() not in stopwords]
          return " ".join(palabras_filtradas)

      texto = remover_stopwords(texto, bolsa_stopwords)

      print(texto)

      # Prediccion Modelo
      new_texts = [texto]
      new_encodings = tokenizer(new_texts, truncation=True, padding=True, max_length=512, return_tensors='pt')
      with torch.no_grad():
          outputs = model(**new_encodings)  # Hacer las predicciones
      predictions = outputs.logits.argmax(dim=-1)  # Obtener las clases predichas
      predicted_labels = [label_mapping[pred] for pred in predictions.tolist()]  # Mapear las predicciones a los nombres de las clases (Consulta vehículo, consulta persona, otra consulta)

      # Asignar el tipo de consulta a la variable correspondiente y llamar la funcion que realiza esa consulta
      result = predicted_labels[0]

      if result==0:
        var_tipoConsulta = "Consulta Persona"
        return consulta_persona()

      elif result==1:
        var_tipoConsulta = "Consulta Vehículo"
        return consulta_vehiculo()
      
      else:
        respuesta = "Tu consulta no puede ser respondida a través de este chat. Intenta usar los enlaces de la página."
        return(f"{respuesta}\n")

# ---------------------------------
# Método para identificar datos
# ---------------------------------
# Patrones regex para los datos alfanuméricos
patron_VIN = r'\b[a-hj-npr-z0-9]{17}\b' # Para VIN alfanumérico de 17 caracteres
#patron_SOAT = r'\b\d{13}\b'  # Para SOAT de 13 dígitos
patron_RTM = r'\b\d{8}\b'  # Para RTM de 8 dígitos
patron_cedula1 = r'\b\d{8}\b'  # Para cédulas de 8 dígitos
patron_cedula2 = r'\b\d{10}\b'  # Para cédulas de 10 dígitos
patron_placa_carro = r'\b[a-z]{3}\d{3}\b'  # Para placas con 3 letras y 3 dígitos
patron_placa_moto = r'\b[a-z]{3}\d{2}[a-z]\b'  # Para placas con 3 letras, 2 dígitos y una letra al final

# Opciones del tipo de documento
opciones_tipo_documento = {
    "Carnet Diplomático": r'\bcarnet diplomatico\b',
    "Cédula de Ciudadanía": r'\bcedula\b|(?:^|\s)cc(?:\s|$)',
    "Cédula de Extranjería": r'\bextranjeria\b',
    "Pasaporte": r'\bpasaporte\b|\bpassport\b',
    "Permiso por Protección Temporal": r'\bpermiso por proteccion temporal\b',
    "Registro Civil": r'\bregistro civil\b',
    "Tarjeta de Identidad": r'\btarjeta de identidad\b|(?:^|\s)ti(?:\s|$)'
}

# Opciones de consulta para la consulta de vehículos
opciones_consultar_por = {
    "Placa y Propietario": r'\bplaca\b|\bpropietario\b',
    "VIN": r'\bvin\b|\bnumero unico de identificacion\b',
    "PVO": r'\bpvo\b|\bplanilla de viaje ocasional\b',
    "Guía de movilidad": r'\bguia de movilidad\b',
    "RTM": r'\brtm\b|\brevision tecnico mecanica\b'
}

# Opciones de aseguradoras para la consulta de vehículos por SOAT
opciones_aseguradora = {
    "ALLIANZ SEGUROS S.A.": r'\ballianz\b',
    "ASEGURADORA SOLIDARIA DE COLOMBIA ENTIDAD COOPERATIVA": r'\baseguradora solidaria\b|\bsolidaria de colombia\b',
    "AXA COLPATRIA SEGUROS SA": r'\baxa\b|\bcolpatria\b',
    "CARDIF COLOMBIA SEGUROS GENERALES SA": r'\bcardif\b',
    "COMPAÑIA MUNDIAL DE SEGUROS SA": r'\bcompañia mundial de seguros\b',
    "HDI SEGUROS COLOMBIA S.A.": r'\bhdi\b',
    "LA EQUIDAD SEGUROS GENERALES ORGANISMO COOPERATIVO": r'\bequidad\b',
    "LA PREVISORA S.A. COMPAÑIA DE SEGUROS": r'\bla previsora\b',
    "MAPFRE SEGUROS GENERALES DE COLOMBIA S.A.": r'\bmapfre\b',
    "SEGUROS COMERCIALES BOLIVAR S.A": r'\bseguros bolivar\b',
    "SEGUROS DEL ESTADO S.A.": r'\bseguros del estado\b',
    "SEGUROS GENERALES SURAMERICANA S.A.": r'\bsuramericana\b',
    "ZURICH COLOMBIA SEGUROS S.A.": r'\bzurich\b'
}

# Metodo para identificar datos, busca en el texto ingresado si existe alguno de los patrones regex definidos
def identificar_datos(texto):
  global var_tipoDocumento, var_numeroDocumento, var_numeroPlaca, var_numeroVIN, var_numeroSOAT, var_consultarPor, var_aseguradora, var_numeroRTM

  # Tipo Documento
  for opcion, patron in opciones_tipo_documento.items():
    if re.search(patron, texto):
      var_tipoDocumento = opcion

  # Cedula
  busqueda = re.search(patron_cedula1, texto)
  if busqueda is not None:
    var_numeroDocumento = busqueda.group()
  
  busqueda = re.search(patron_cedula2, texto)
  if busqueda is not None:
    var_numeroDocumento = busqueda.group()

  # Consulta Vehiculo - Consultar por
  for opcion, patron in opciones_consultar_por.items():
    if re.search(patron, texto):
      var_consultarPor = opcion

  # Placa
  busqueda = re.search(patron_placa_carro, texto)
  if busqueda is not None:
    var_numeroPlaca = busqueda.group()
  
  busqueda = re.search(patron_placa_moto, texto)
  if busqueda is not None:
    var_numeroPlaca = busqueda.group()

  # VIN
  busqueda = re.search(patron_VIN, texto)
  if busqueda is not None:
    var_numeroVIN = busqueda.group()

  # SOAT
  #busqueda = re.search(patron_SOAT, texto)
  #if busqueda is not None:
  #  var_numeroSOAT = busqueda.group()

  # Aseguradora
  #for opcion, patron in opciones_aseguradora.items():
  #  if re.search(patron, texto):
  #    var_aseguradora = opcion

  # RTM
  busqueda = re.search(patron_RTM, texto)
  if busqueda is not None:
    var_numeroRTM = busqueda.group()
  
# ---------------------------------
# Método Consulta Persona
# ---------------------------------
def consulta_persona():
  if (var_tipoDocumento == "") and (var_numeroDocumento == ""):
    respuesta = "Indica el tipo y número de documento del propietario. Ejemplo: \"Cédula 1234567890\""
    return(f"{respuesta}\n")
  
  elif var_tipoDocumento == "":
    respuesta = "Indica el tipo de documento del propietario. Ejemplo: \"Cédula\""
    return(f"{respuesta}\n")
  
  elif var_numeroDocumento == "":
    respuesta = "Indica el número de documento del propietario. Ejemplo: \"1234567890\""
    return(f"{respuesta}\n")
  
  else:
    return query_persona()

# ---------------------------------
# Método Consulta Vehículo
# ---------------------------------
def consulta_vehiculo():
  match var_consultarPor:
    case "Placa y Propietario":
      if (var_numeroPlaca == "") and (var_tipoDocumento == "") and (var_numeroDocumento == ""):
        respuesta = "Indica la placa del vehículo y el tipo y número de documento del propietario. Ejemplo: \"AWX123 Cédula 1234567890\""
        return(f"{respuesta}\n")

      elif (var_numeroPlaca == "") and (var_tipoDocumento == ""):
        respuesta = "Indica la placa del vehículo y el tipo de documento del propietario. Ejemplo: \"AWX123 Cédula\""
        return(f"{respuesta}\n")
      
      elif (var_numeroPlaca == "") and (var_numeroDocumento == ""):
        respuesta = "Indica la placa del vehículo y el número de documento del propietario. Ejemplo: \"AWX123 1234567890\""
        return(f"{respuesta}\n")
      
      elif (var_tipoDocumento == "") and (var_numeroDocumento == ""):
        respuesta = "Indica el tipo y número de documento del propietario. Ejemplo: \"Cédula 1234567890\""
        return(f"{respuesta}\n")
      
      elif var_numeroPlaca == "":
        respuesta = "Indica la placa del vehículo. Ejemplo: \"AWX123\""
        return(f"{respuesta}\n")

      elif var_tipoDocumento == "":
        respuesta = "Indica el tipo de documento del propietario. Ejemplo: \"Cédula\""
        return(f"{respuesta}\n")
      
      elif var_numeroDocumento == "":
        respuesta = "Indica el número de documento del propietario. Ejemplo: \"1234567890\""
        return(f"{respuesta}\n")
      
      else:
        return query_vehiculo()

    case "VIN":
      if var_numeroVIN == "":
        respuesta = "Indica el número VIN del vehículo. Ejemplo: \"1HGCM82633A123456\""
        return(f"{respuesta}\n")
      
      else:
        return query_vehiculo()

    case "SOAT":
      if (var_numeroSOAT == "") and (var_aseguradora == ""):
        respuesta = "Indica el número del SOAT y la aseguradora que emitió la póliza"
        return(f"{respuesta}\n")
      
      elif var_numeroSOAT == "":
        respuesta = "Indica el número del SOAT"
        return(f"{respuesta}\n")
      
      elif var_aseguradora == "":
        respuesta = "Indica la aseguradora que emitió la póliza"
        return(f"{respuesta}\n")
      
      else:
        return query_vehiculo()

    case "PVO":
      if var_numeroPlaca == "":
        respuesta = "Indica la placa del vehículo. Ejemplo: \"AWX123\""
        return(f"{respuesta}\n")
      
      else:
        return query_vehiculo()
      
    case "Guía de movilidad":
      if var_numeroPlaca == "":
        respuesta = "Indica la placa del vehículo. Ejemplo: \"AWX123\""
        return(f"{respuesta}\n")
      
      else:
        return query_vehiculo()

    case "RTM":
      if var_numeroRTM == "":
        respuesta = "Indica el número de certificado RTM. Ejemplo: \"12345678\""
        return(f"{respuesta}\n")
      
      else:
        return query_vehiculo()

    case _:
      respuesta = "Indica cómo quieres hacer la consulta: por Placa y Propietario, Número VIN, o Número RTM"
      return(f"{respuesta}\n")

# ---------------------------------
# Query Consulta Persona
# ---------------------------------
def query_persona():
  global var_finalizo_consulta

  excel_file = 'data/Datos_Dummy_Personas.xlsx'
  df = pd.read_excel(excel_file, dtype=str)

  result = df[(df['Tipo_Documento_Propietario'] == var_tipoDocumento) & 
              (df['Numero_Documento_Propietario'] == var_numeroDocumento)]

  # Si se encontró algún resultado, se genera el preview y/o el PDF
  if not result.empty:
    selected_columns = ["Nombre Completo", "Tipo_Documento_Propietario", "Numero_Documento_Propietario", "Estado Persona", "Fecha de Inscripcion"]
    filtered_df = result.loc[:, selected_columns]
    filtered_df.columns = ["Nombre Completo", "Tipo Documento", "Numero Documento", "Estado de la persona", "Fecha de inscripción"]

    json_result = filtered_df.to_json(orient="records", date_format="iso", force_ascii=False)
    pdf_file_path = generate_pdf(result)

    response_data = {
        "text": json_result[1: -1],
        "pdf_url": pdf_file_path
    }
    
    var_finalizo_consulta = True
    return JSONResponse(content=response_data)
  # Si no, se retorna el mensaje de error acorde a la consulta realizada
  else:
    return("No se ha encontrado la persona en estado ACTIVA o SIN REGISTRO. Datos consultados: tipo de documento " + var_tipoDocumento + " y número de documento " + var_numeroDocumento + ".")

# ---------------------------------
# Query Consulta Vehículo
# ---------------------------------
respuestas_error_vehiculos = {
    "Placa y Propietario": "Los datos registrados no corresponden con los propietarios activos para el vehículo consultado.",
    "VIN": "Señor Usuario, para el vehículo consultado no hay información registrada en el sistema RUNT.",
    "SOAT": "Señor Usuario, para el vehículo consultado no hay información registrada en el sistema RUNT.",
    "PVO": "Señor Usuario no existe información de PVO para el vehículo consultado.",
    "Guía de movilidad": "Señor Usuario, para el vehículo consultado no hay información registrada en el sistema RUNT.",
    "RTM": "Señor Usuario, para el vehículo consultado no hay información registrada en el sistema RUNT."
}

def query_vehiculo():
  global var_finalizo_consulta

  excel_file = 'data/Datos_Dummy_Vehiculos.xlsx'
  df = pd.read_excel(excel_file, dtype=str)

  match var_consultarPor:
    case "Placa y Propietario":
      result = df[(df['Numero de placa'].str.upper() == var_numeroPlaca.upper()) & 
                  (df['Tipo_Documento_Propietario'].str.upper() == var_tipoDocumento.upper()) & 
                  (df['Numero_Documento_Propietario'].str.upper() == var_numeroDocumento.upper())]
    case "VIN":
      result = df[(df['Numero de VIN'].str.upper() == var_numeroVIN.upper())]
    case "SOAT":
      result = df[(df['Poliza Soat'].str.upper() == var_numeroSOAT.upper())]
    case "PVO":
      result = df[(df['Numero de placa'].str.upper() == var_numeroPlaca.upper())]
    case "Guía de movilidad":
      result = df[(df['Numero de placa'].str.upper() == var_numeroPlaca.upper())]
    case "RTM":
      result = df[(df['Numero Certificado RTM'].str.upper() == var_numeroRTM.upper())]

  # Si se encontró algún resultado, se genera el preview y/o el PDF
  if not result.empty:
    selected_columns = ["Numero de placa", "Tipo_Servicio", "Clase Vehiculo"]
    filtered_df = result.loc[:, selected_columns]
    filtered_df.columns = ["PLACA DEL VEHÍCULO", "Tipo de servicio", "Clase de vehículo"]

    json_result = filtered_df.to_json(orient="records", date_format="iso", force_ascii=False)
    pdf_file_path = generate_pdf(result)

    response_data = {
        "text": json_result[1: -1],
        "pdf_url": pdf_file_path
    }
    
    var_finalizo_consulta = True
    return JSONResponse(content=response_data)

  # Si no, se retorna el mensaje de error acorde a la consulta realizada
  else:
    match var_consultarPor:
      case "Placa y Propietario":
        return(respuestas_error_vehiculos["Placa y Propietario"] + " Datos consultados: placa " + var_numeroPlaca.upper() + ", tipo de documento " + var_tipoDocumento.upper() + " y número de documento " + var_numeroDocumento.upper() + ".")
      case "VIN":
        return(respuestas_error_vehiculos["VIN"] + " Datos consultados: VIN " + var_numeroVIN.upper() + ".")
      case "SOAT":
        return(respuestas_error_vehiculos["SOAT"] + " Datos consultados: SOAT " + var_numeroSOAT.upper() + ".")
      case "PVO":
        return(respuestas_error_vehiculos["PVO"] + " Datos consultados: placa " + var_numeroPlaca.upper() + ".")
      case "Guía de movilidad":
        return(respuestas_error_vehiculos["Guía de movilidad"] + " Datos consultados: placa " + var_numeroPlaca.upper() + ".")
      case "RTM":
        return(respuestas_error_vehiculos["RTM"] + " Datos consultados: RTM " + var_numeroRTM.upper() + ".")

# ---------------------------------
# Generador de PDF
# ---------------------------------
def generate_pdf(result):
  buffer = BytesIO()
  doc = SimpleDocTemplate(buffer, pagesize=letter)

  # Cargar la imagen del logo
  logo = Image("./assets/logo_mintransporte.png", width=181, height=109)  # Ajusta el tamaño según sea necesario

  # Configurar la posición de la imagen (en la parte superior central)
  logo.hAlign = 'CENTER'
  logo.vAlign = 'TOP'

  space_between_logo_and_table = Spacer(1, 20)

  data = [['Campo', 'Valor']]
  for column in result.columns:
      for value in result[column]:
          data.append([column, value])

  table = Table(data)

  style = TableStyle([
      ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f57338")),
      ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
      ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
      ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
      ('FONTSIZE', (0, 0), (-1, 0), 14),
      ('BOTTOMPADDING', (0, 0), (-1, 0), 9),
      ('TOPPADDING', (0, 0), (-1, 0), 3),
      ('GRID', (0, 0), (-1, -1), 1, colors.black),
  ])

  num_rows = len(data)
  # Aplica colores alternados dinámicamente
  for i in range(1, num_rows):  # Empieza en 1 para saltarse el encabezado
      if i % 2 == 1:
          style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor("#FBE4D5"))
      else:
          style.add('BACKGROUND', (0, i), (-1, i), colors.white)

  table.setStyle(style)

  doc.build([logo, space_between_logo_and_table, table])
  buffer.seek(0)

  # Guarda el archivo en la carpeta /reports
  timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
  unique_id = uuid.uuid4().hex
  pdf_filename = f"generated_report_{timestamp}_{unique_id}.pdf"
  pdf_file_path = f"./reports/{pdf_filename}"

  if not os.path.exists("./reports"):
      os.makedirs("./reports")

  with open(pdf_file_path, 'wb') as f:
      f.write(buffer.read())

  return pdf_filename  # Devuelve la ruta del PDF generado

# ---------------------------------
# Nueva consulta
# ---------------------------------
@app.post("/new")
def read_root():
  global var_tipoConsulta, var_tipoDocumento, var_numeroDocumento, var_procedencia, var_consultarPor, var_numeroPlaca, var_numeroVIN, var_numeroSOAT, var_aseguradora, var_numeroRTM, var_finalizo_consulta
  
  var_tipoConsulta = ""

  # Consulta Persona
  var_tipoDocumento = ""
  var_numeroDocumento = ""

  # Consulta Vehículo
  var_procedencia = "Nacional" # Por defecto
  var_consultarPor = ""
  var_numeroPlaca = ""
  var_numeroVIN = ""
  var_numeroSOAT = ""
  var_aseguradora = ""
  var_numeroRTM = ""

  var_finalizo_consulta = False

# ---------------------------------
# Descargar PDF
# ---------------------------------
@app.get("/reports/{filename}")
def download_file(filename: str):
  file_path = f"./reports/{filename}"
  file = open(file_path, "rb")
  return StreamingResponse(file, media_type="application/pdf")

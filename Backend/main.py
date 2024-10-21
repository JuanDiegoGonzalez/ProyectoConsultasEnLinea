from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from joblib import load
from DataModel import DataModel

from transformers import BertTokenizer
import re
import unicodedata
import torch
import pandas as pd

import pandas as pd

# ---------------------------------
# Preparación del modelo y CORS
# ---------------------------------

app = FastAPI()
model = load("assets/trained_bert_model.joblib")

data = pd.read_excel('assets/Datos de entrenamiento.xlsx')
labels = data['Intención'].tolist()
label_mapping = list(set(labels))  # Unique label names from the training dataset

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
var_numeroDocumento = "" # TODO

# Consulta Vehículo
var_procedencia = "Nacional" # Default
var_consultarPor = ""
var_numeroPlaca = ""
var_numeroVIN = "" # TODO
var_numeroSOAT = "" # TODO
var_aseguradora = "" ###
var_numeroRTM = "" # TODO

# ---------------------------------
# Hilo principal
# ---------------------------------

@app.post("/talk")
def talk(input: DataModel):
  identificar_datos(input.texto)

  if var_tipoConsulta == "":
    return make_predictions(input)
  
  elif var_tipoConsulta == "Consulta Persona":
    return consulta_persona()
  
  elif var_tipoConsulta == "Consulta Vehículo":
    return consulta_vehiculo()

# ---------------------------------
# Método para predecir la intención
# ---------------------------------
def make_predictions(input: DataModel):
    global var_tipoConsulta

  # Tokenize new input texts for prediction
    new_texts = [input.texto]
    new_encodings = tokenizer(new_texts, truncation=True, padding=True, max_length=512, return_tensors='pt')

    # Make predictions
    with torch.no_grad():
        outputs = model(**new_encodings)

    # Get the predicted labels
    predictions = outputs.logits.argmax(dim=-1)

    # Map predictions to label names
    predicted_labels = [label_mapping[pred] for pred in predictions.tolist()]

    # Print the predicted label for each input text
    for i, text in enumerate(new_texts):
        result = predicted_labels[i]

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

patron_cedula1 = r'\b\d{8}\b'  # Para cédulas de 8 dígitos
patron_cedula2 = r'\b\d{10}\b'  # Para cédulas de 10 dígitos
patron_placa_carro = r'\b[A-Z]{3}\d{3}\b'  # Para placas con 3 letras y 3 dígitos
patron_placa_moto = r'\b[A-Z]{3}\d{2}[A-Z]\b'  # Para placas con 3 letras, 2 dígitos y una letra al final

opciones_tipo_documento = {
    "Carnet Diplomático": r'\bcarnet\b|\bdiplomatico\b',
    "Cédula de Ciudadanía": r'\bcedula\b|\bciudadania\b',
    "Cédula de Extranjería": r'\bextranjeria\b',
    "Pasaporte": r'\bpasaporte\b',
    "Permiso por Protección Temporal": r'\bpermiso\b|\bproteccion\b|\btemporal\b',
    "Registro Civil": r'\bregistro\b|\bcivil\b',
    "Tarjeta de Identidad": r'\btarjeta\b|\bidentidad\b'
}

opciones_consultar_por = {
    "Placa y Propietario": r'\bplaca\b|\bpropietario\b',
    "VIN (Número único de identificación)": r'\bvin\b|\bnumero\b|\bunico\b|\bindentificacion\b',
    "SOAT": r'\bsoat\b',
    "PVO (Planilla de viaje ocasional)": r'\bpvo\b|\bplanilla\b|\bviaje\b|\bocasional\b',
    "Guía de movilidad": r'\bguia\b|\bmovilidad\b',
    "RTM": r'\brtm\b'
}

opicones_aseguradora = {
    "ALLIANZ SEGUROS S.A.": r'\ballianz\b',
    "ASEGURADORA SOLIDARIA DE COLOMBIA ENTIDAD COOPERATIVA": r'\bsolidaria\b|\bcooperativa\b|\bcolombia\b|\bentidad\b',
    "AXA COLPATRIA SEGUROS SA": r'\baxa\b|\bcolpatria\b',
    "CARDIF COLOMBIA SEGUROS GENERALES SA": r'\bcardif\b',
    "COMPAÑIA MUNDIAL DE SEGUROS SA": r'\bmundial\b',
    "HDI SEGUROS COLOMBIA S.A.": r'\bhdi\b',
    "LA EQUIDAD SEGUROS GENERALES ORGANISMO COOPERATIVO": r'\bequidad\b|\bcooperativo\b',
    "LA PREVISORA S.A. COMPAÑIA DE SEGUROS": r'\bprevisora\b',
    "MAPFRE SEGUROS GENERALES DE COLOMBIA S.A.": r'\bmapfre\b',
    "SEGUROS COMERCIALES BOLIVAR S.A": r'\bbolivar\b|\bcomerciales\b',
    "SEGUROS DEL ESTADO S.A.": r'\bestado\b',
    "SEGUROS GENERALES SURAMERICANA S.A.": r'\bsuramericana\b',
    "ZURICH COLOMBIA SEGUROS S.A.": r'\bzurich\b'
}

def identificar_datos(texto):
  global var_tipoDocumento, var_numeroDocumento, var_numeroPlaca, var_consultarPor, var_aseguradora

  texto = unicodedata.normalize('NFD', texto)
  texto = texto.encode('ascii', 'ignore').decode('utf-8')
  texto = texto.lower()

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

  # Aseguradora
  for opcion, patron in opicones_aseguradora.items():
    if re.search(patron, texto):
      var_aseguradora = opcion
  
# ---------------------------------
# Método Consulta Persona
# ---------------------------------
def consulta_persona():
  if (var_tipoDocumento == "") and (var_numeroDocumento == ""):
    respuesta = "Indica el tipo y número de documento del propietario"
    return(f"{respuesta}\n")
  
  elif var_tipoDocumento == "":
    respuesta = "Indica el tipo de documento del propietario"
    return(f"{respuesta}\n")
  
  elif var_numeroDocumento == "":
    respuesta = "Indica el número de documento del propietario"
    return(f"{respuesta}\n")
  
  else:
    # TODO: Hacer consulta persona
    return query_persona()

# ---------------------------------
# Método Consulta Vehículo
# ---------------------------------
def consulta_vehiculo():
  match var_consultarPor:
    case "Placa y Propietario":
      if (var_numeroPlaca == "") and (var_tipoDocumento == "") and (var_numeroDocumento == ""):
        respuesta = "Indica la placa del vehículo y el tipo y número de documento del propietario"
        return(f"{respuesta}\n")

      if (var_numeroPlaca == "") and (var_tipoDocumento == ""):
        respuesta = "Indica la placa del vehículo y el tipo de documento del propietario"
        return(f"{respuesta}\n")
      
      if (var_numeroPlaca == "") and (var_numeroDocumento == ""):
        respuesta = "Indica la placa del vehículo y el número de documento del propietario"
        return(f"{respuesta}\n")
      
      if (var_tipoDocumento == "") and (var_numeroDocumento == ""):
        respuesta = "Indica el tipo y número de documento del propietario"
        return(f"{respuesta}\n")
      
      elif var_numeroPlaca == "":
        respuesta = "Indica la placa del vehículo"
        return(f"{respuesta}\n")

      elif var_tipoDocumento == "":
        respuesta = "Indica el tipo de documento del propietario"
        return(f"{respuesta}\n")
      
      elif var_numeroDocumento == "":
        respuesta = "Indica el número de documento del propietario"
        return(f"{respuesta}\n")
      
      else:
        # TODO: Hacer consulta placa y propietario
        ...

    case "VIN":
      if var_numeroPlaca == "":
        respuesta = "Indica el número VIN del vehículo"
        return(f"{respuesta}\n")
      
      else:
        # TODO: Hacer consulta VIN
        ...

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
        # TODO: Hacer consulta SOAT
        ...

    case "PVO":
      if var_numeroPlaca == "":
        respuesta = "Indica la placa del vehículo"
        return(f"{respuesta}\n")
      
      else:
        # TODO: Hacer consulta PVO
        ...
      
    case "Guía de movilidad":
      if var_numeroPlaca == "":
        respuesta = "Indica la placa del vehículo"
        return(f"{respuesta}\n")
      
      else:
        # TODO: Hacer consulta Guia de Movilidad
        ...

    case "RTM":
      if var_numeroRTM == "":
        respuesta = "Indica el número de certificado RTM"
        return(f"{respuesta}\n")
      
      else:
        # TODO: Hacer consulta RTM
        ...
      
    case _:
      respuesta = "Indica cómo quieres hacer la consulta: por Placa y Propietario, VIN, SOAT, PVO, Guía de movilidad o RTMN"
      return(f"{respuesta}\n")

# ---------------------------------
# Query Consulta Persona
# ---------------------------------
def query_persona():
  excel_file = 'data/Datos_Dummy_Personas.xlsx'
  df = pd.read_excel(excel_file, dtype=str)

  result = df[(df['Tipo_Documento_Propietario'] == var_tipoDocumento) & 
              (df['Numero_Documento_Propietario'] == var_numeroDocumento)]

  if not result.empty:
      return("Se encontró el siguiente registro:" + result.to_string(index=False))
  else:
      return("No se ha encontrado la persona en estado ACTIVA o SIN REGISTRO")

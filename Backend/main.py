from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from joblib import load
from DataModel import DataModel

from transformers import BertTokenizer
import torch
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
var_numeroDocumento = ""

# Consulta Vehículo
var_procedencia = "Nacional" # Default
var_consultarPor = "" # "Placa y Propietario" # Default
var_numeroPlaca = ""
var_numeroVIN = ""
var_numeroSOAT = ""
var_aseguradora = ""
var_numeroRTM = ""

# ---------------------------------
# Hilo principal
# ---------------------------------

@app.post("/talk")
def talk(input: DataModel):
  # TODO: identificar_datos()

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
    ...

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
        # TODO: Hacer consulta persona
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
      respuesta = "Indica cómo quieres hacer la consulta: por Placa y Propietario, VIN, SOAT, PVO, Guía de movilidad o RTMN)"
      return(f"{respuesta}\n")

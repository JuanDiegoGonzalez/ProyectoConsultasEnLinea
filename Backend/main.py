from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from joblib import load
from DataModel import DataModel

from transformers import BertTokenizer
import torch
import pandas as pd

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

@app.get("/")
def read_root():
   return {"Hello": "World"}

@app.get("/integrantes")
def intgrantes():
   return "Juan Ignacio Arbelaez Velez, Brenda Catalina Barahona Pinilla y Juan Diego Gonzalez Gomez"

@app.post("/predict")
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
      tipoConsulta = ""
      if result==0:
        tipoConsulta = "Consulta Persona"
      elif result==1:
        tipoConsulta = "Consulta Vehículo"
      elif result==2:
        tipoConsulta = "Otra Consulta"
      return(f"{predicted_labels[i]} - {tipoConsulta}\n")

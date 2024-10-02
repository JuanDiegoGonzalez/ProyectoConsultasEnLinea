from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from joblib import load
from DataModel import DataModel
from Preparation import prepare
import pandas as pd
from sklearn.metrics import r2_score

app = FastAPI()
model = load("assets/modeloP1E2.joblib")

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
def make_predictions(row: DataModel):
   df = pd.DataFrame(row.dict(), columns=row.dict().keys(), index=[0])
   df.columns = row.columns()

   try:
      new_df = prepare(df)
      result = model.predict(new_df)
      return result.tolist()[0]
   except:
      return -1

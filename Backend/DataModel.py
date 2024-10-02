from typing import List
from pydantic import BaseModel

'''
class Row(BaseModel):
    # Estas varibles permiten que la librería pydantic haga el parseo entre el Json recibido y el modelo declarado.

    label: str
    study_and_condition: str

    #Esta función retorna los nombres de las columnas correspondientes con el modelo esxportado en joblib.
    def columns(self):
        return ["label", "study_and_condition"]
'''

class DataModel(BaseModel):
    study_and_condition: str

    #Esta función retorna los nombres de las columnas correspondientes con el modelo esxportado en joblib.
    def columns(self):
        return ["study_and_condition"]

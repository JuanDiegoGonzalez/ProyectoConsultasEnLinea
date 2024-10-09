from pydantic import BaseModel

'''
class texto(BaseModel):
    # Esta varible permite que la librería pydantic haga el parseo entre el Json recibido y el modelo declarado.
    label: str
'''

class DataModel(BaseModel):
    texto: str

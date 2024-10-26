from pydantic import BaseModel
from typing import Literal, Optional

'''
class texto(BaseModel):
    # Esta varible permite que la librería pydantic haga el parseo entre el Json recibido y el modelo declarado.
    label: str
'''

class DataModel(BaseModel):
    texto: str


class ConsultaVehiculo(BaseModel):
    """
        Modelo base inicial para la consulta de vehiculos. 
        Clase padre porque todas las consultas necesitan al menos esto
    """
    procedencia: Optional[Literal["nacional", "extranjero", "diplomatico"]] = "extranjero"
    tipo_consulta_vehiculo: Optional[Literal["placa_propietario", "vin", "soat", "pvo", "guia_movilidad","rtm"]] = "placa_propietario"


class ConsultaVehiculoPP(ConsultaVehiculo):
    """
        Modelo para las consulta de vehiculo con placa y propietario
    """
    numero_placa:str
    tipo_documento:str
    num_doc_propietario:str

class ConsultaVehiculoVIN(ConsultaVehiculo):
    """
        Modelo para las consulta de vehiculo con placa y propietario
    """
    numero_vin:int

class ConsultaVehiculoSOAT(ConsultaVehiculo):
    """
        Modelo para las consulta de vehiculo con SOAT
        En teoria la aseguradora es un Literal
    """
    numero_soat:int
    aseguradora:str

class ConsultaVehiculoPVO(ConsultaVehiculo):
    """
        Modelo para las consulta de vehiculo con PVO
    """
    numero_pvo:int

class ConsultaVehiculoGuiaMovildiad(ConsultaVehiculo):
    """
        Modelo para las consulta de vehiculo con Guia de Movildiad
    """
    guia_movilidad:int

class ConsultaVehiculoRTM(ConsultaVehiculo):
    """
        Modelo para las consulta de vehiculo con RTM
    """
    rtm:int


class ConsultaPersonas(BaseModel):
    """
        Modelo base inicial para la consulta de personas 

        TODO: Esto deberia estar igual de abstraido a las consultas vehiculo, es decir
        una clase por tipo de informacion
    """
    numero_documento: str
# Proyecto Consultas en Línea

## Integrantes:
* Juan Ignacio Arbelaez Velez

* Brenda Catalina Barahona Pinilla

* Juan Diego Gonzalez Gomez

## Instrucciones de instalación

1. Clonar o descargar el repositorio:

  ```shell
  git clone https://github.com/
  ```

2. Abrir el proyecto en Visual Studio Code o el IDE de su preferencia

## Instrucciones de despliegue del API (Backend)

1. Luego de clonar el repositorio, abrir una terminal (del IDE elegido) y abrir la carpeta "Backend" (estando en la carpeta del proyecto):

  ```shell
  cd Backend
  ```

2. Instalar los requerimientos:

  ```shell
  py -3.10 -m venv venv
  cd .\venv\
  cd .\Scripts\
  .\Activate.ps1
  cd ..
  cd ..
  pip install -r requirements.txt
  ```

3. Ejecutar el programa en la terminal:

  ```shell
  uvicorn main:app --reload
  ```

4. Se podrá verificar el funcionamiento del programa ingresando desde un navegador a la URL http://127.0.0.1:8000/ (se debe visualizar un objeto JSON: "{"Hello":"World"}")

## Instrucciones de ejecución de la aplicación web:

1. Abrir la carpeta "Frontend" desde el explorador de archivos y darle doble click izquierdo al archivo chatbot.html. Si no abre de esta forma, intentar con click derecho > abrir con > seleccionar el explorador web de su preferencia.

2. Nótese que se debe haber desplegado el API (Backend) como se indicó anteriormente para que la aplicación web funcione correctamente.

import mysql.connector #IMPORTAMOS EL MODULO PARA REALIZAR LA CONEXION CON MYSQL
import click #CLICK NOS PERMITE EJECUTAR NUESTROS PROPIOS COMANDOS DESDE LA TERMINAL, PARA QUERYS SQL
from flask import current_app, g #current_app hace referencia a la aplicación flask, g constante sin valor. 
from flask.cli import with_appcontext #Nos permite acceder a variables de configuarción de nuestra app.
from .schema import instructions #SCRIPTS NECESARIOS PARA MYSQL

def get_db(): #Realiza la conexión con la base de datos. Y devuelve la misma, además del cursor.
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host = current_app.config['DATABASE_HOST'],
            user = current_app.config['DATABASE_USER'],
            password = current_app.config['DATABASE_PASSWORD'],
            database = current_app.config['DATABASE']
        )
        g.c = g.db.cursor(dictionary=True) #Almacena los datos obtenidos dentro de un diccionario 
    return g.db,g.c

def close_db(e=None): #Cierra la conexión con la base de datos. 
    db = g.pop('db',None)

    if db is not None:
        db.close()

def init_db(): #Nos ejecuta las querys del archivo instructions.    
    db, c = get_db() #Almacena los valores que retorna la función get_db()
    for i in instructions:
        c.execute(i) #FOR que ejecuta individualmente las querys de inicialización para la base de datos. 
    db.commit()

#Decorador que indica el comando en terminal para ejecutar la función subsecuente.#flask 'command' para ejecutar./antes de ejecutar flask run.  
@click.command('init-db')
@with_appcontext #Permite usar las variables de entorno al ejecutar la función subsecuente.
def init_db_command():
    init_db()
    click.echo('Base de datos inicializada.')#Al ejecutar un comando click, retorna en terminal el msj

def init_app(app): #Obtiene los datos de nuestra app, y son accesibles para las instrucciones subsecuentes. 
    app.teardown_appcontext(close_db) #Cada vez que termine la ejecución de una petición, 
                                      #o acabemos de llamar a un endpoint ejecuta la función 
    app.cli.add_command(init_db_command) #Suscribir comando a nuestra aplicación, 
                                         #para ejecutarse con su configuración 
    
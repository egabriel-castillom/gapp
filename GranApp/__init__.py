#ACTIVAMOS EL entorno virtual. venv/Scripts/. activate
#PREPARAMOS EL ENTORNO VIRTUAL. en el folder principal install flask, mysql-connector-python, werkzeug.
#Asignamos permisos a nuestro user en MYSQL. /Admin/Schema-Priv/addentry/selectall/apply.
#Creamos mainappfolder/__init__.py., éste archivo es tomado como el modulo de inicio de nuestra app, el folder como la app en si con acceso a archivos hermanos.  
#DENTRO DE /todo ... export | FLASK_ENV = development, FLASK_DEBUG=1 ,FLASK_APP = todo(folder de init app), flask run. |  
import os #Permite utilizar variables de entorno.
from flask import Flask #importas el framework pre instalado en el entorno virtual.
from dotenv import load_dotenv
load_dotenv()
def create_app(): #SE EJECUTA SIEMPRE QUE SE GENERE UNA INSTANCIA DE LA APLICACIÓN dentro del bash. 
    app = Flask(__name__) #Asigna modulo inicial para nuestra aplicación.
   
    app.config.from_mapping( #Configuración de nuestra app, obtiene las variables de entorno necesarias para ejecutar conexion con db.  
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        DATABASE_HOST = os.environ.get('FLASK_DATABASE_HOST'), #os.environ son variables de entorno obtenidas de os.
        DATABASE_USER = os.environ.get('FLASK_DATABASE_USER'), #las cuales son definidas antes de la ejecución a través del bash.
        DATABASE_PASSWORD = os.environ.get('FLASK_DATABASE_PASSWORD'),
        DATABASE = os.environ.get('FLASK_DATABASE'),                        
    )

    from . import tododb #Pasamos la configuarción de nuestra app y se ejecuta la función tododb.init_app.  
    tododb.init_app(app)      

    from . import auth #Registramos auth.bp a nuestra app para poder acceder a las instrucciones.
    app.register_blueprint(auth.bp) 

    from . import todo
    app.register_blueprint(todo.bp)

    from . import mail
    app.register_blueprint(mail.bp)

    import click
    @app.before_first_request
    def bf():
        tododb.init_db()
        click.echo('Se ha reiniciado la base de datos we')
        
    return app    

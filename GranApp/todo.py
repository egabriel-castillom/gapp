from webbrowser import get
#LA LIBRERIA DE FLASK OFRECE PAQUETES QUE TE BRINDAN UN CONTEXTO
#PARA LA APLICACION. Con 'g', podemos almacenar recursos que son
# accesibles durante la ejecucion de actividades.
from flask import (
    Blueprint, flash,   g, redirect, render_template, request, url_for 
)
from werkzeug.exceptions import abort #Cuando intenta hacer una acción no permitida
from .auth import login_required
from .tododb import get_db
from datetime import datetime

bp = Blueprint('todo', __name__)

def get_todo(id): #Obtener registro todo dado el id.
    db,c = get_db()
    c.execute(
        '''select t.id, t.description, t.completed, t.created_by, t.created_at, u.username from 
        todo t join usuario u on t.created_by = u.id where t.id = %s''',
        (id,) 
    )

    todo = c.fetchone() #Almacena el primer registro coincidente
    if todo is None: #De no haber ningún registro, aborta la solicitud hacia una página de error.
        abort(404,'El todo de id {0} no existe'.format(id))

    return todo #Devuelve el registro.     

@bp.route('/')
@login_required#Valida que g.user tenga un valor.
def index(): #Después de validar el inicio de sesión, muestra la página principal de 'Todo' LIST. 
    db, c = get_db() 
    # Trae los datos de los registros que compartan el mismo valor en t.created_by y u.id (mismo usuario).
    #Selecciona las columnas con alias.columna Renombras las tablas con alias y relacionamos sus columnas 
    #ordenandolas por fechas descendentes.     
    c.execute( 
        '''select t.id, t.description, u.username, t.completed, t.created_at, t.completed_at from todo t JOIN usuario u 
        on t.created_by = u.id where t.created_by = %s order by created_at desc'''
    , (g.user['id'],)) #Con where id = g.user['id'], todos los elementos están ligados a g.user, el usuario en sesión. 
    todos = c.fetchall()#Ejecuta y almacena todos los resultados
    return render_template('todo/index.html', todos=todos) #Devuelve la plantilla incluyendo los registros.

@bp.route('/create', methods=('GET', 'POST'))
@login_required #Valida que g.user tenga un valor.
def create(): #Después de validar el inicio de sesión, se muestra la página de creación de un NUEVO Todo. 
    if request.method == 'POST': #Si se envía el formulario, se recibe el método POST. 
        descripcion = request.form.get('descripcion') #Almacenamos la descripción introducida
        error = None

        if not descripcion: 
            error = 'La descripción es requerida.'

        if error is not None: #De no haber introducido una descripción muestra el error con un flash en pantalla.
            flash(error)
        else:
            db, c = get_db() #Si hay una descripción, crea un nuevo registro 
            c.execute(
                'insert into todo (description, completed, created_by)'
                'values(%s,%s,%s)',
                (descripcion,False,g.user['id'])
            )        
            db.commit()
            return redirect(url_for('todo.index'))

    return render_template('todo/create.html') #Devuelve la plantilla con el formulario de creación 

@bp.route('/<int:id>/update', methods=('GET', 'POST')) 
@login_required
def update(id): #Actualizar todo, con el id que proporciona el link html del elemento seleccionado.
    todo = get_todo(id)
    if request.method == 'POST': #Si se guarda el todo
        description = request.form.get('description') #Almacena la nueva descripción
        #Checkbox se evalúa verdadero si el estado es 'on', de no ser así es False.  
        completed = True if request.form.get('completed') == 'on' else False#Almacena el nuevo estado
        if completed == True:
            time = datetime.now()
            db,c = get_db()
            c.execute(
                'update todo set completed_at=%s where id = %s ', (time,id)
            )
        error = None
        if not description: 
            error = 'La descripción es requerida.'
        if error is not None: #De no haber ningúna descripción, muestra el error con un flash en pantalla
            flash(error)
        else:
            db , c = get_db()
            c.execute(
                'update todo set description = %s, completed= %s where id = %s and created_by = %s',
                (description, completed, id, g.user['id'])
            )        
            db.commit()
            return redirect(url_for('todo.index')) #Al haber actualizado el registro, vuelve a la página principal

    return render_template('todo/update.html', todo = todo) #Mostrar plantilla con el todo corresponiente al id.     

@bp.route('/<int:id>/delete', methods=('GET','POST'))
@login_required
def delete(id): #Eliminar el todo corresponiente al id que proporciona el link html del elemento seleccionado.
    db, c = get_db()
    c.execute(
        'delete from todo where id = %s and created_by =%s',(id,g.user['id'])
    )
    db.commit()
    return redirect(url_for('todo.index'))#Al haber eliminado el registro, vuelve a la pantalla principal.    

########################################  A D M I N  ########################################

@bp.route('/master')
def masterIndex(): #Muestra la página principal de 'Todo' LIST registrados por cada usuario. 
    db, c = get_db() 
    # Trae los datos de los registros que compartan el mismo valor en t.created_by y u.id (mismo usuario).
    #Selecciona las columnas con alias.columna Renombras las tablas con alias y relacionamos sus columnas 
    #ordenandolas por fechas descendentes.     
    c.execute( 
        '''select t.id, t.description, u.username, t.completed, t.created_at, t.completed_at from todo t JOIN usuario u on t.created_by = u.id where t.created_by > 0 order by created_at desc''')
    todos = c.fetchall()#Ejecuta y almacena todos los resultados
    return render_template('todo/master.html', todos=todos) #Devuelve la plantilla incluyendo los registros.
    #return str(todos)

@bp.route('/<int:id>/masterUpdate', methods=('GET', 'POST')) 
def masterUpdate(id): #Actualizar todo, con el id que proporciona el link html del elemento seleccionado.
    todo = get_todo(id)
    if request.method == 'POST': #Si se guarda el todo
        description = request.form.get('description') #Almacena la nueva descripción
        #Checkbox se evalúa verdadero si el estado es 'on', de no ser así es False.  
        completed = True if request.form.get('completed') == 'on' else False#Almacena estado
        if completed == True:
            time = datetime.now()
            db,c = get_db()
            c.execute(
                'update todo set completed_at=%s where id = %s ', (time,id)
            )
        error = None
        if not description: 
            error = 'La descripción es requerida.'
        if error is not None: #De no haber ningúna descripción, muestra el error con un flash en pantalla
            flash(error)
        else:
            db , c = get_db()
            c.execute(
                'update todo set description = %s, completed= %s where id = %s',
                (description, completed, id)
            )        
            db.commit()
            return redirect(url_for('todo.masterIndex')) #Al haber actualizado el registro, vuelve a la página principal

    return render_template('todo/updateMaster.html', todo = todo) #Mostrar plantilla con el todo corresponiente al id.     

@bp.route('/<int:id>/masterDelete', methods=('GET','POST'))
def masterDelete(id): #Eliminar el todo corresponiente al id que proporciona el link html del elemento seleccionado.
    db, c = get_db()
    c.execute('delete from todo where id = %s',(id,))
    db.commit()
    return redirect(url_for('todo.masterIndex'))#Al haber eliminado el registro, vuelve a la pantalla principal.    

@bp.route('/masterUser',methods=('GET','POST'))
def masterUser():
    db, c = get_db()
    c.execute('select id, username from usuario')
    users = c.fetchall()
    return render_template('masterUser.html', users = users)

@bp.route('/<int:id>/userUpdate', methods=('GET', 'POST')) 
def userUpdate(id): #Actualizar todo, con el id que proporciona el link html del elemento seleccionado.
    db, c = get_db()
    c.execute('select * from usuario where id = %s', (id,))
    user = c.fetchone()
    if request.method == 'POST': #Si se guarda el todo
        newUsername = request.form.get('username') #Almacena el nueno nombre
        error = None
        if not newUsername: 
            error = 'El nombre es requerido.'
        if error is not None: #De no haber ningúna descripción, muestra el error con un flash en pantalla
            flash(error)
        else:
            db , c = get_db()
            c.execute(
                'update usuario set username = %s where id = %s',
                (newUsername, id)
            )        
            db.commit()
            return redirect(url_for('todo.masterUser')) #Al haber actualizado el registro, vuelve a la página principal
    return render_template('updateUser.html', user = user) #Mostrar plantilla con el todo corresponiente al id.     

@bp.route('/<int:id>/deleteUser', methods=('GET','POST'))
def deleteUser(id):
    if request.method == 'POST':
        db,c = get_db()
        c.execute('delete from todo where created_by = %s', (id,))
        db.commit()
        c.execute('delete from usuario where id = %s', (id,))
        db.commit()        
        return redirect(url_for('todo.masterUser'))

##    return  str(user)
#@bp.route('/adm
# indb', methods=('GET','POST'))
#@login_required
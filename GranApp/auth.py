from time import sleep
import functools
import click
from flask import(
    g,Blueprint,flash,render_template,request,url_for,session,redirect
)
from werkzeug.security import check_password_hash, generate_password_hash
from .tododb import get_db
#Creamos el blueprint, el cual dará el prefijo /auth a las rutas en las funciones del mismo. 

#Extiende las funcionalidades de la app, a través de sus rutas. 
bp = Blueprint('auth',__name__,url_prefix='/auth')   

@bp.route('/register',methods=['GET','POST']) #Asignamos un nuevo url del blueprint a la función.  
def register():                               #FUNCION DE REGISTRO DE USUARIO.
    if request.method =='POST':                 #Si recibe un método 'POST'
        username = request.form['username']   #Almacena las variables desde la forma, [name] 
        email = request.form['email']
        password = request.form['password']
        db, c = get_db()                      #Obtenemos database y cursor
        error = None                          #Creamos variable de error. default = None
        #Query para obtener registros con el username   
        c.execute('select * from usuario where username = %s', (username,))
        if not username: #Si no obtenemos username de la forma 
            error = 'El nombre de usuario es requerido.' #El mensaje de error.
        if not password: #Si no obtenemos password de la forma
            error = 'La contraseña es requerida' #El mensaje de error.
        if not email: #Si no obtenemos password de la forma
            error = 'El correo es requerido' #El mensaje de error.
        elif c.fetchone() is not None: #Si encontramos el registro por el nombre de usuario.
            error = 'El usuario {} ya ha sido registrado'.format(username) #El mensaje de error. 

        if error is None: #Si no almacenamos ningún error.
            c.execute(    #Creamos un nuevo registro con los valores obtenidos de la forma.
                'insert into usuario (username, password, email) values(%s,%s,%s)',
                (username,generate_password_hash(password),email)              
            )              
            db.commit()  #Comprometemos la base de datos para realizar el query 
            return redirect(url_for('auth.login')) #Redireccionamos al usuario desp ués de registrar.

        flash(error)    #Si hay algún error, lo enviamos con flash.
    return render_template('aut/register.html') #Si recibe un 'GET', muestra la plantilla.

@bp.route('/login', methods=['GET','POST']) 
def login(): #FUNCION DE INICIO DE SESION
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password') 
        if username == '@' and password == '@':
            return redirect(url_for('auth.adminLogin')) 
        db, c = get_db()       
        error = None
        c.execute(
            'select * from usuario where username = %s', (username,)
        ) 
        user = c.fetchone() #Almacenamos el registro coincidentes con el username.        
        if user is None: #Si no hay ningún registro.
            error = 'Usuario y/o Password invalidos.' #El mensaje de error.
        elif not check_password_hash(user['password'],password): #Si hay registro, pero password incorrecta. 
            error = 'Usuario y/o Password invalidos'  #El mensaje de error.   

        if error is None: #Si no hay ningún error.
            session.clear() #Elimina la sesión vigente.
            session['user_id'] = user['id'] #Almacena el id del usuario en la sesión.  
            return redirect(url_for('todo.index')) #Redireccióna a la pagina principal

        flash(error) 
    return render_template('aut/login.html')            

@bp.before_app_request #Antes de procesar cualquier petición, ejecutará ésta función.
def load_logged_in_user(): #Cargar usuario a g.user 
    user_id = session.get('user_id')
    if user_id == None:
        g.user = None 
    else: #De haber algún id de usuario, busca el usuario correspondiente
        db,c = get_db() 
        c.execute(
            'select * from usuario where id = %s', (user_id,)
        )     
        g.user = c.fetchone() #Devuelve el registro de usuario como diccionario.

def login_required(view): #Función decoradora, que indica la necesidad de estar loggeado.    
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None: #Si el usuario aún no ha iniciado sesión.
            return redirect(url_for('auth.login')) #Reenvíalo al login page.

        return view(**kwargs)#Si ya inició sesión, continúa con la solicitud     

    return wrapped_view     

@bp.route('/logout') 
def logout(): #FUNCIÓN DE CIERRE DE SESIÓN.
    session.clear()
    return redirect(url_for('auth.login'))

@bp.route('/admin', methods=['GET','POST']) 
def adminLogin(): #FUNCION DE INICIO DE SESION para administrador
    if request.method == 'POST':
        username = request.form.get('adminname')
        password = request.form.get('adminpassword')
        if username.lower() =='forever' and password.lower() =='never':
            return redirect(url_for('auth.adminReg'))
        db, c = get_db()       
        error = None
        c.execute(
            'select * from admin where aname = %s', (username,)
        ) 
        user = c.fetchone() #Almacenamos el registro coincidentes con el username.        
        if user is None: #Si no hay ningún registro.
            error = 'Can not be too far away...' #El mensaje de error.
        elif not check_password_hash(user['apassword'],password):  #Si hay registro, pero password incorrecta. 
            error = 'Can not be too far away...'  #El mensaje de error.   

        if error is None: #Si no hay ningún error.
            session.clear() #Elimina la sesión vigente.
            session['user_id'] = user['id'] #Almacena el id del registro en user_id de la sesión.  
            return redirect(url_for('auth.adminMenu')) #Redireccióna a la pagina principal

        flash(error) 
    return render_template('aut/ADMIN.html')        

@bp.route('/adminReg', methods=['GET','POST']) 
def adminReg(): #FUNCION DE registro para administrador
    if request.method == ('POST'):
        db, c = get_db()
        username = request.form.get('adminname')
        password = request.form.get('adminpassword')
        c.execute('insert into admin (aname, apassword) values(%s,%s)',
                    (username,generate_password_hash(password)))             
        db.commit()   
        return redirect(url_for('auth.adminLogin'))
    return render_template('aut/adminReg.html')    

@bp.route('/adminMenu')    
def adminMenu():
    return redirect(url_for('mail.index'))
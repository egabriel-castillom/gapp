from time import sleep 
import todo.tododb as tdb       
from werkzeug.security import generate_password_hash
################################
def adminReg():                            
    db, c = tdb.get_db()
    username = 'GABRIELC'
    password = 'NUNC4m13nt!'                     
    c.execute('insert into admin (aname, apassword) values(%s,%s)',
                (username,generate_password_hash(password)))             
    db.commit()   
    print('REGISTRADO EXITOSAMENTE')
    sleep(.5) 
    print('Confirmando registros..')
    c.execute('select * from admin')
    nuevoReg = c.fetchall()
    print(nuevoReg)

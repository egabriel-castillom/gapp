import os
import smtplib
import ssl
from email.message import EmailMessage
from flask import Blueprint, current_app, render_template, request, flash,redirect,url_for
from .tododb import get_db # .db - MODULO EN CARPETA HERMANA
from dotenv import load_dotenv
load_dotenv()

bp = Blueprint('mail',__name__,url_prefix=('/'))

@bp.route('/mailIndex', methods=['GET'])
def index():
    search = request.args.get('search')    
    db, c = get_db()
    if search is None:
        c.execute('SELECT * FROM email;')
    else:
        c.execute('SELECT * FROM email WHERE content like %s;', ('%' + search + '%',))
    mailList = c.fetchall()    
    return render_template('mails/mail.html', mails = mailList)
    #return str(mailList)

@bp.route('/mailCreate', methods=['GET','POST'])
def create():
    db,c = get_db()
    c.execute('SELECT * FROM usuario;')
    regUsuarios = c.fetchall()
    if request.method == 'POST':
        adress = request.form.get('adress')
        subject = request.form.get('subject')
        content = request.form.get('content')
        errors = []
        if not adress:
            errors.append('Es requerida una direccion de correo.')
        if not subject:
            errors.append('Es requerido que se agrege un asunto para el correo.')
        if not content:
            errors.append('Es requerido que se agregue el contenido para el correo.')
        if len(errors) == 0:
            send(adress,subject,content)
            db,c = get_db()
            c.execute('INSERT INTO email (email,subject,content) VALUES(%s,%s,%s)',(adress,subject,content))
            db.commit()
            return redirect(url_for('mail.index'))
        else:
            for error in errors:
                flash(error)
    return render_template('mails/crear.html', regUsuarios = regUsuarios)
########################################################
def send(to,subject,content):

    # Define email sender and receiver
    email_sender = os.environ.get('gmailAdress')
    email_password = os.environ.get('gmailPassword')
    email_receiver = to

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(content)

    # Add SSL (layer of security)
    context = ssl.create_default_context()

    # Log in and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
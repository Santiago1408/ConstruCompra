from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

db_config = {
    'user': 'laurafernandez',
    'password': 'mysqladmin',
    'host': 'laurafernandez.mysql.pythonanywhere-services.com',
    'database': 'laurafernandez$marketplace',
}

def get_db_connection():
   
    return mysql.connector.connect(**db_config)


@app.route('/')
def logueo():
    return render_template('Logueo.html')

@app.route('/iniciar_sesion', methods=['POST'])
def iniciar_sesion():
    usuario = request.form['usuario']
    contrasena = request.form['contra']

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)


    cursor.execute("SELECT * FROM usuarios WHERE correo = %s", (usuario,))
    usuario_db = cursor.fetchone()
    if usuario == 'admin' and contra == '1234':
        return redirect(url_for('dashboard'))
    else:
        return 'Usuario o contraseña incorrectos'
def enviar_correo_recuperacion(destinatario, token):
    """Envía el correo de recuperación de contraseña."""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Recuperación de contraseña - ConstruCompra'
        msg['From'] = MAIL_USERNAME
        msg['To'] = destinatario
        link_recuperacion = url_for('restablecer_password', token=token, _external=True)
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #df8755;">Recuperación de contraseña - ConstruCompra</h2>
                <p>Has solicitado restablecer tu contraseña. Haz clic en el siguiente enlace para continuar:</p>
                <p>
                    <a href="{link_recuperacion}"
                       style="background-color: #df8755;
                              color: white;
                              padding: 10px 20px;
                              text-decoration: none;
                              border-radius: 5px;">
                        Restablecer contraseña
                    </a>
                </p>
                <p>Este enlace expirará en 1 hora por seguridad.</p>
                <p>Si no solicitaste este cambio, puedes ignorar este correo.</p>
                <p style="color: #666; font-size: 12px;">Este es un correo automático, por favor no responder.</p>
            </body>
        </html>
        """
        parte_html = MIMEText(html, 'html')
        msg.attach(parte_html)
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)

        return True
    except Exception as e:
        logger.error(f"Error enviando correo: {str(e)}")
        return False

@app.route('/solicitar_recuperacion', methods=['POST'])
def solicitar_recuperacion():
    try:
        metodo = request.form['metodo']
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        if metodo == 'email':
            correo = request.form.get('correo')
            if not correo:
                return jsonify(success=False,
                             message="Por favor, ingresa un correo electrónico válido.")

            cursor.execute("SELECT * FROM usuarios WHERE correo = %s", (correo,))
            if not cursor.fetchone():
                return jsonify(success=False,
                             message="El correo no está registrado en el sistema.")

            token = serializer.dumps(correo, salt='recuperar-password')
            if enviar_correo_recuperacion(correo, token):
                return jsonify(success=True,
                             message="Se han enviado las instrucciones a tu correo.")
            else:
                return jsonify(success=False,
                             message="Error al enviar el correo. Intenta más tarde.")
        else:
            return jsonify(success=False,
                         message="Método de recuperación no válido.")

    except Exception as e:
        logger.error(f"Error en solicitar_recuperacion: {str(e)}")
        return render_template('errorSolicitudes.html')
    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()

@app.route('/dashboard')
def dashboard():
    return 'Bienvenido al dashboard'

if __name__ == '__main__':
    app.run(debug=True)


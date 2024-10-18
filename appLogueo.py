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

    if usuario == 'admin' and contra == '1234':
        return redirect(url_for('dashboard'))
    else:
        return 'Usuario o contraseña incorrectos'

@app.route('/dashboard')
def dashboard():
    return 'Bienvenido al dashboard'

if __name__ == '__main__':
    app.run(debug=True)


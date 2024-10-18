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
def iniciar_sesion():
    return render_template('Logueo.html')

@app.route('/iniciar_sesion', methods=['POST'])
def login():
    usuario = request.form['usuario']
    contra = request.form['contra']

    if usuario == 'admin' and contra == '1234':
        return redirect(url_for('dashboard'))
    else:
        return 'Usuario o contraseña incorrectos'

@app.route('/dashboard')
def dashboard():
    return 'Bienvenido al dashboard'

if __name__ == '__main__':
    app.run(debug=True)


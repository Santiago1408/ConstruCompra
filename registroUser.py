from flask import Flask, render_template, request, redirect, url_for
import pymysql
from datetime import datetime

app = Flask(__name__)

# Conexión a la base de datos MySQL en PythonAnywhere
def get_db_connection():
    return pymysql.connect(
        host='florenciaRamos.mysql.pythonanywhere-services.com',
        user='florenciaRamos',
        password='Polenpro060803',
        db='florenciaRamos$marketplace'
    )

@app.route('/', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        fecha_nacimiento = request.form['fecha_nacimiento']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        correo = request.form['correo']
        contrasenia = request.form['password']
        genero = request.form['genero']

        # Conectar a la base de datos
        connection = get_db_connection()
        cursor = connection.cursor()

        # Insertar nuevo usuario en la base de datos
        query = '''
            INSERT INTO usuarios (nombre, fecha_nacimiento, genero, direccion, telefono, correo, contrasenia)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(query, (nombre, fecha_nacimiento, genero, direccion, telefono, correo, contrasenia))

        # Confirmar la transacción
        connection.commit()

        # Cerrar la conexión
        cursor.close()
        connection.close()

    correo_invalido = request.args.get('correo_invalido', False)

if __name__ == '__main__':
    app.run(debug=True)

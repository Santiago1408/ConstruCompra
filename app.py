from flask import Flask, render_template, request, redirect
import pymysql

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
        # Obtener los datos del formulario
        nombre = request.form['nombre']
        fecha_nacimiento = request.form['fecha_nacimiento']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        correo = request.form['correo']
        contrasenia = request.form['password']
        genero = request.form['genero']

        # Conectar a la base de datos y guardar los datos
        connection = get_db_connection()
        cursor = connection.cursor()

        # Consulta SQL para insertar los datos en la tabla Usuario
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

        # Redirigir al mismo formulario después de registrar los datos
        return redirect('/')

    # Renderizar la plantilla del formulario
    return render_template("registro.html")

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

# Configuración de la conexión a la base de datos
db_config = {
    'user': 'laurafernandez',
    'password': 'mysqladmin',
    'host': 'laurafernandez.mysql.pythonanywhere-services.com',
    'database': 'laurafernandez$marketplace',
}

def get_db_connection():
    """Establece la conexión a la base de datos."""

    return mysql.connector.connect(**db_config)

@app.route('/')
def editar_producto():
    # Conectar a la base de datos y obtener un producto aleatorio
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos ORDER BY RAND() LIMIT 1;")
    producto = cursor.fetchone()

    if producto is None:
        return "No se encontró ningún producto", 404

    cursor.close()
    conn.close()

    return render_template('Interfaz.html', producto=producto)


# Ruta para abrir el archivo "Interfaz.html"
@app.route('/interfaz')
def interfaz():
    return render_template('Interfaz.html')

if __name__ == '__main__':
    app.run(debug=True)

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

# Ruta para abrir el archivo "Interfaz.html"
@app.route('/interfaz')
def interfaz():
    return render_template('Interfaz.html')

if __name__ == '__main__':
    app.run(debug=True)

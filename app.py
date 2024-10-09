from flask import Flask, render_template
import pymysql  # Asegúrate de que pymysql está instalado y funcionando

app = Flask(__name__)

# Función para conectar a la base de datos
def conectarBD():
    return pymysql.connect(
        host="josue1408.mysql.pythonanywhere-services.com",
        user="josue1408",
        password="sANTIAGO1408",
        database="josue1408$ConstruCompra1",
        cursorclass=pymysql.cursors.DictCursor  # Para obtener resultados en formato diccionario
    )

@app.route('/')
def index():
    try:
        # Conectar a la base de datos
        conn = conectarBD()
        cursor = conn.cursor()

        # Ejecutar consulta SQL para obtener productos
        cursor.execute("SELECT nombre, descripcion, precio FROM productos")
        productos = cursor.fetchall()  # Obtener todos los productos

        conn.close()  # Cerrar la conexión

        # Pasar los productos al template
        return render_template('index.html', productos=productos)

    except Exception as e:
        return f"Error en la base de datos: {e}"

if __name__ == '__main__':
    app.run(debug=True)




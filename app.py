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


@app.route('/guardar_producto', methods=['POST'])
def guardar_producto():
    datos = request.get_json()

    # Debug: imprimir los datos recibidos
    print("Datos recibidos:", datos)

    id_producto = datos['id_producto']
    nombre = datos['nombre']
    descripcion = datos['descripcion']
    precio = datos['precio']
    cantidad = datos['cantidad']
    tipo_venta = datos['tipo_venta']
    ubicacion = datos['ubicacion']
    marca = datos['marca']
    color = datos['color']
    tamano = datos['tamano']

    conn = mysql.connector.connect(**db_config) 
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE productos
            SET nombre = %s, descripcion = %s, precio = %s, cantidad = %s, tipo_venta = %s,
                ubicacion = %s, marca = %s, color = %s, tamano = %s
            WHERE id_producto = %s
        """, (nombre, descripcion, precio, cantidad, tipo_venta, ubicacion, marca, color, tamano, id_producto))

        conn.commit()
        print("Actualización exitosa en la base de datos")

        # Enviar respuesta en formato JSON al cliente
        return jsonify({"status": "success", "message": "Cambios guardados exitosamente"}), 200
    except Exception as e:
        print("Error al actualizar:", str(e))
        conn.rollback()
        return jsonify({"status": "error", "message": "Hubo un problema al realizar los cambios"}), 500
    finally:
        cursor.close()
        conn.close()



# Ruta para abrir el archivo "Interfaz.html"
@app.route('/interfaz')
def interfaz():
    return render_template('Interfaz.html')

if __name__ == '__main__':
    app.run(debug=True)

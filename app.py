from flask import Flask, render_template, request, jsonify
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
    return mysql.connector.connect(**db_config)

@app.route('/editar_producto/<int:id_producto>')
def editar_producto(id_producto):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos WHERE id_producto = %s", (id_producto,))
    producto = cursor.fetchone()

    if producto is None:
        return "No se encontró ningún producto", 404

    cursor.close()
    conn.close()

    return render_template('Interfaz.html', producto=producto)

@app.route('/guardar_producto', methods=['POST'])
def guardar_producto():
    datos = request.get_json()
    print("Datos recibidos:", datos)

    id_producto = datos['id_producto']
    nombre = datos['nombre']
    descripcion = datos['descripcion']
    precio = datos['precio']  # Asegúrate de limpiar la unidad "Bs." si es necesario
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
        return jsonify({"status": "success", "message": "Cambios guardados exitosamente"}), 200
    except Exception as e:
        print("Error al actualizar:", str(e))
        conn.rollback()
        return jsonify({"status": "error", "message": "Hubo un problema al realizar los cambios"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/mis_publicaciones')
def mis_publicaciones():
    if 'id_usuario' not in session:
        return redirect(url_for('logueo'))  # Redirigir si no ha iniciado sesión

    # Obtener el ID del usuario de la sesión
    id_usuario = session['id_usuario']

    # Consultar los productos asociados a este usuario
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = '''
        SELECT id_producto, nombre, descripcion, precio
        FROM productos
        WHERE id_usuarios = %s
    '''
    cursor.execute(query, (id_usuario,))
    productos = cursor.fetchall()

    cursor.close()
    connection.close()

    # Pasar los productos al HTML
    return render_template('mis_publicaciones.html', productos=productos)


if __name__ == '__main__':
    app.run(debug=True)

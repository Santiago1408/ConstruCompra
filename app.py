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
    try:
        if 'id_usuario' not in session:
            return redirect(url_for('logueo'))

        id_usuario = session['id_usuario']

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Consulta del perfil del usuario con los campos correctos
        query_usuario = '''
            SELECT nombre, fecha_nacimiento, direccion, telefono, correo, genero
            FROM usuarios
            WHERE id_usuarios = %s
        '''
        cursor.execute(query_usuario, (id_usuario,))
        usuario = cursor.fetchone()

        if not usuario:
            return "Usuario no encontrado", 404

        # Consulta de productos del usuario
        query_productos = '''
            SELECT id_producto, nombre, descripcion, precio
            FROM productos
            WHERE id_usuarios = %s
        '''
        cursor.execute(query_productos, (id_usuario,))
        productos = cursor.fetchall()

        cursor.close()
        connection.close()

        # Pasamos el perfil del usuario y sus productos al template
        return render_template('mis_publicaciones.html', usuario=usuario, productos=productos)

    except Exception as e:
        print(f"Error: {e}")  # Ver error en consola
        return "Ocurrió un error en el servidor", 500

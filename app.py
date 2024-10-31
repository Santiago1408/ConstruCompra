from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import mysql.connector
from datetime import datetime
import bcrypt;
from io import BytesIO
from PIL import Image
import base64

app = Flask(__name__)
# Hashea la contraseña

app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 MB
app.secret_key = '4629ee957597b108fccfb9b9f1489c16'  # Asegúrate de que sea segura
hashed_password = bcrypt.hashpw(app.secret_key.encode('utf-8'), bcrypt.gensalt())

# Configuración de la conexión a la base de datos
db_config = {
    'user': 'proyectocibernau',
    'password': 'mysqladmin',
    'host': 'proyectocibernautas.mysql.pythonanywhere-services.com',
    'database': 'proyectocibernau$marketplace',
}

@app.route('/filtrar_productos', methods=['POST'])
def filtrar_productos():
    data = request.get_json()
    precio_min = data.get('precioMin', 0)
    precio_max = data.get('precioMax', None)
    marca = data.get('marca', '').strip()

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Construir consulta con filtros
    query = "SELECT id_producto, nombre, descripcion, precio FROM productos WHERE 1=1"
    params = []

    if precio_min:
        query += " AND precio >= %s"
        params.append(precio_min)
    if precio_max:
        query += " AND precio <= %s"
        params.append(precio_max)
    if marca:
        query += " AND marca LIKE %s"
        params.append(f"%{marca}%")

    cursor.execute(query, params)
    productos_filtrados = cursor.fetchall()
    cursor.close()
    connection.close()

    # Renderizar productos en HTML
    productos_html = render_template('index.html', productos=productos_filtrados)
    return jsonify({'html': productos_html})

def get_db_connection():
    """Establece la conexión a la base de datos."""
    return mysql.connector.connect(**db_config)

# Ruta para la página de inicio de sesión
@app.route('/')
def logueo():
    return render_template('Logueo.html')

@app.template_filter('b64encode')
def b64encode_filter(image):
    if image:
        return base64.b64encode(image).decode('utf-8')
    return None


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        try:
            # Obtener los datos del formulario
            nombre = request.form['nombre']
            fecha_nacimiento = request.form['fecha_nacimiento']
            direccion = request.form['direccion']
            telefono = request.form['telefono']
            correo = request.form['correo']
            contrasenia = request.form['password']
            genero = request.form['genero']
            foto_perfil = request.files.get('foto_perfil')

            # Validar que el usuario tenga al menos 18 años
            fecha_nacimiento_dt = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
            edad = (datetime.now() - fecha_nacimiento_dt).days // 365
            if edad < 18:
                return redirect(url_for('registro', menor_de_edad='true'))

            # Verificar si el correo es @gmail.com
            if not correo.endswith('@gmail.com'):
                return redirect(url_for('registro', correo_invalido='true'))

            # Conectar a la base de datos
            connection = get_db_connection()
            cursor = connection.cursor()

            # Verificar si el correo ya existe
            query_check_email = 'SELECT COUNT(*) FROM usuarios WHERE correo = %s'
            cursor.execute(query_check_email, (correo,))
            result = cursor.fetchone()
            if result[0] > 0:
                cursor.close()
                connection.close()
                return redirect(url_for('registro', correo_existente='true'))

            # Hashear la contraseña
            hashed_password = bcrypt.hashpw(contrasenia.encode('utf-8'), bcrypt.gensalt())

            # Procesar la foto de perfil si fue subida
            foto_perfil_data = None
            if foto_perfil:
                image = Image.open(foto_perfil)
                image = image.convert("RGB").resize((150, 150))  # Redimensionar según necesidades
                img_io = BytesIO()
                image.save(img_io, format='JPEG')
                foto_perfil_data = img_io.getvalue()

            # Insertar nuevo usuario en la base de datos
            query = '''
                INSERT INTO usuarios (nombre, fecha_nacimiento, genero, direccion, telefono, correo, contrasenia, foto_perfil)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(query, (nombre, fecha_nacimiento, genero, direccion, telefono, correo, hashed_password, foto_perfil_data))

            # Confirmar la transacción
            connection.commit()

            # Cerrar la conexión
            cursor.close()
            connection.close()

            # Redirigir a la página con el modal de éxito
            return redirect(url_for('registro', registro_exitoso='true'))

        except Exception as e:
            print("Error en el registro:", str(e))
            return redirect(url_for('registro', error='true'))

    # Obtener los mensajes de error y éxito del registro
    correo_existente = request.args.get('correo_existente', False)
    correo_invalido = request.args.get('correo_invalido', False)
    registro_exitoso = request.args.get('registro_exitoso', False)
    menor_de_edad = request.args.get('menor_de_edad', False)

    return render_template("Registro.html", correo_existente=correo_existente, correo_invalido=correo_invalido, registro_exitoso=registro_exitoso, menor_de_edad=menor_de_edad)


@app.route('/producto/<int:id_producto>', methods=['GET'])
def obtener_producto(id_producto):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*, u.nombre as nombre_usuario, u.id_usuarios as id_vendedor, u.foto_perfil
        FROM productos p
        JOIN usuarios u ON p.id_usuarios = u.id_usuarios
        WHERE p.id_producto = %s
    """, (id_producto,))
    producto = cursor.fetchone()
    cursor.close()
    conn.close()

    if producto:
        # Convertir la foto de perfil BLOB a base64
        if producto['foto_perfil']:
            producto['foto_perfil'] = base64.b64encode(producto['foto_perfil']).decode('utf-8')  # convertimos BLOB a base64
        return jsonify(producto)
    else:
        return jsonify({'error': 'Producto no encontrado'}), 404

# Ruta para la interfaz del producto
@app.route('/interfaz/<int:id_producto>')
def editar_producto(id_producto):
    if 'id_usuario' not in session:
        return redirect(url_for('logueo'))  # Redirigir al inicio de sesión si no ha iniciado sesión

    id_usuario = session['id_usuario']

    # Conectar a la base de datos y obtener el producto con el id_producto para este usuario
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM productos WHERE id_producto = %s AND id_usuarios = %s", (id_producto, id_usuario))
    producto = cursor.fetchone()

    cursor.close()
    conn.close()

    if producto is None:
        return "No se encontró el producto para este usuario", 404

    return render_template('EditarProducto.html', producto=producto)

@app.route('/guardar_producto', methods=['POST'])
def guardar_producto():
    if 'id_usuario' not in session:
        return jsonify({"status": "error", "message": "Usuario no autenticado"}), 403

    datos = request.get_json()

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

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE productos
            SET nombre = %s, descripcion = %s, precio = %s, cantidad = %s, tipo_venta = %s,
                ubicacion = %s, marca = %s, color = %s, tamano = %s
            WHERE id_producto = %s AND id_usuarios = %s
        """, (nombre, descripcion, precio, cantidad, tipo_venta, ubicacion, marca, color, tamano, id_producto, session['id_usuario']))

        conn.commit()
        return jsonify({"status": "success", "message": "Cambios guardados exitosamente"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/index')
def index():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Obtener la información del usuario logueado
        user_id = session.get('id_usuario')  # Obtener el ID del usuario de la sesión
        usuario_info = None
        if user_id:
            cursor.execute("SELECT nombre, foto_perfil FROM usuarios WHERE id_usuarios = %s", (user_id,))
            usuario_info = cursor.fetchone()

            # Convertir la foto de perfil a base64 si existe
            if usuario_info and usuario_info['foto_perfil']:
                usuario_info['foto_perfil'] = base64.b64encode(usuario_info['foto_perfil']).decode('utf-8')

        cursor.execute("SELECT id_producto, nombre, descripcion, precio FROM productos")
        productos = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('index.html', productos=productos, usuario_info=usuario_info)

    except mysql.connector.Error as err:
        return f"Error en la base de datos: {err}"

@app.route('/iniciar_sesion', methods=['POST'])
def iniciar_sesion():
    usuario = request.form['usuario']
    contrasena = request.form['contra']

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Consulta para verificar si el usuario y la contraseña son correctos
    cursor.execute("SELECT * FROM usuarios WHERE correo = %s", (usuario,))
    usuario_db = cursor.fetchone()

    if usuario_db:
        if bcrypt.checkpw(contrasena.encode('utf-8'), usuario_db['contrasenia'].encode('utf-8')):
            session['id_usuario'] = usuario_db['id_usuarios']  # Guardar el ID del usuario en la sesión
            return jsonify(success=True, message="Credenciales correctas.")
        else:
            return jsonify(success=False, message="Contraseña incorrecta.")
    else:
        return jsonify(success=False, message="El correo no está registrado.")


@app.route('/registrar_producto', methods=['GET', 'POST'])
def registrar_producto():
    if request.method == 'GET':
        return render_template('RegistrarProducto.html')

    if 'id_usuario' not in session:
        return jsonify({'status': 'error', 'message': 'Usuario no autenticado'}), 403

    try:
        id_usuario = session['id_usuario']
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        cantidad = request.form['cantidad']
        tipo_venta = request.form['tipo_venta']
        ubicacion = request.form['ubicacion']
        marca = request.form['marca']
        color = request.form['color']
        tamano = request.form['tamano']

        connection = get_db_connection()
        cursor = connection.cursor()

        query = '''
            INSERT INTO productos (id_usuarios, nombre, descripcion, cantidad, tipo_venta, precio, ubicacion, marca, color, tamano)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(query, (id_usuario, nombre, descripcion, cantidad, tipo_venta, precio, ubicacion, marca, color, tamano))

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'status': 'success', 'message': 'Producto registrado exitosamente'}), 200
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'status': 'error', 'message': 'Error al registrar el producto'}), 500



@app.route('/mis_publicaciones', methods=['GET'])
def mis_publicaciones():
    try:
        if 'id_usuario' not in session:
            return redirect(url_for('logueo'))

        id_usuario = session['id_usuario']

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

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

        # Si la solicitud es AJAX, devolver solo la lista de publicaciones
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template('partial_publicaciones.html', productos=productos)

        # Si no es AJAX, renderizar la página completa
        return render_template('mis_publicaciones.html', productos=productos)

    except Exception as e:
        print(f"Error: {e}")  # Ver error en consola
        return "Ocurrió un error en el servidor", 500


@app.route('/ver_perfil')
def ver_perfil():
    if 'id_usuario' not in session:
        return redirect(url_for('logueo'))

    return redirect(url_for('ver_perfil_usuario', user_id=session['id_usuario']))

@app.route('/edicionUsr')
def edicionUsr():
    if 'id_usuario' not in session:
        return redirect(url_for('logueo'))  # Redirige si no hay sesión

    id_usuario = session['id_usuario']

    try:
        # Intentamos conectarnos a la base de datos y ejecutar la consulta
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = '''
            SELECT nombre, fecha_nacimiento, genero, direccion, telefono, correo, foto_perfil
            FROM usuarios
            WHERE id_usuarios = %s
        '''
        cursor.execute(query, (id_usuario,))
        datos_usuario = cursor.fetchone()

        cursor.close()
        connection.close()

        # Verificar si se encontró un usuario
        if datos_usuario is None:
            return "No se encontró el usuario", 404

        # Renderizar la plantilla con los datos del usuario
        return render_template('edicionUsr.html', datos_usuario=datos_usuario)

    except Exception as e:
        # Capturar errores inesperados y mostrarlos en el log
        print(f"Error en edicionUsr: {e}")
        return "Ocurrió un error interno en el servidor", 500

@app.route('/eliminar_producto/<int:id_producto>', methods=['POST'])
def eliminar_producto(id_producto):
    if 'id_usuario' not in session:
        return jsonify({'status': 'error', 'message': 'Usuario no autenticado'}), 403

    id_usuario = session['id_usuario']

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Elimina el producto de la base de datos si pertenece al usuario actual
        cursor.execute("DELETE FROM productos WHERE id_producto = %s AND id_usuarios = %s", (id_producto, id_usuario))
        connection.commit()

        return jsonify({'status': 'success', 'message': 'Producto eliminado exitosamente'}), 200
    except Exception as e:
        connection.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/ver_perfil/<int:user_id>')
def ver_perfil_usuario(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = '''
        SELECT nombre, fecha_nacimiento, genero, direccion, telefono, correo, foto_perfil
        FROM usuarios
        WHERE id_usuarios = %s
    '''
    cursor.execute(query, (user_id,))
    datos_usuario = cursor.fetchone()
    cursor.close()
    connection.close()

    # Verificar si el usuario que está viendo el perfil es el dueño
    is_owner = 'id_usuario' in session and session['id_usuario'] == user_id

    return render_template('ver_perfil.html', datos_usuario=datos_usuario, is_owner=is_owner)


if __name__ == '__main__':
    app.run(debug=True)

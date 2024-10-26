from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import mysql.connector
from datetime import datetime
import bcrypt;
from io import BytesIO
from PIL import Image
import base64

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 MB
app.secret_key = '4629ee957597b108fccfb9b9f1489c16'  # Asegúrate de que sea segura
hashed_password = bcrypt.hashpw(app.secret_key.encode('utf-8'), bcrypt.gensalt())


# Configuración de la conexión a la base de datos
db_config = {
    'user': 'laurafernandez',
    'password': 'mysqladmin',
    'host': 'laurafernandez.mysql.pythonanywhere-services.com',
    'database': 'laurafernandez$marketplace',
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.template_filter('b64encode')
def b64encode_filter(image):
    if image:
        return base64.b64encode(image).decode('utf-8')
    return None


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

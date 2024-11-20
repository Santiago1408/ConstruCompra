from flask import Flask, render_template, request, redirect, url_for, jsonify, session, Response
import mysql.connector
from datetime import datetime
import bcrypt;
from io import BytesIO
from PIL import Image
import base64
import os
from flask import current_app
from itsdangerous import URLSafeTimedSerializer
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import re


app = Flask(__name__)
# Hashea la contraseña

app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
app.secret_key = '4629ee957597b108fccfb9b9f1489c16'
hashed_password = bcrypt.hashpw(app.secret_key.encode('utf-8'), bcrypt.gensalt())

app.config['SECRET_KEY'] = '4629ee957597b108fccfb9b9f1489c16'
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USERNAME = "proyecto.cibernautass@gmail.com"
MAIL_PASSWORD = "qqso rqai kuee tyeb"
MAIL_USE_TLS = True

db_config = {
    'user': 'proyectocibernau',
    'password': 'mysqladmin',
    'host': 'proyectocibernautas.mysql.pythonanywhere-services.com',
    'database': 'proyectocibernau$marketplace',
}

def get_db_connection():
    """Establece la conexión a la base de datos."""
    return mysql.connector.connect(**db_config)

@app.route('/')
def logueo():
    return render_template('Logueo.html')

@app.template_filter('b64encode')
def b64encode_filter(image):
    if image:
        return base64.b64encode(image).decode('utf-8')
    return None

def enviar_correo_recuperacion(destinatario, token):
    """Envía el correo de recuperación de contraseña."""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Recuperación de contraseña - ConstruCompra'
        msg['From'] = MAIL_USERNAME
        msg['To'] = destinatario
        link_recuperacion = url_for('restablecer_password', token=token, _external=True)
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #df8755;">Recuperación de contraseña - ConstruCompra</h2>
                <p>Has solicitado restablecer tu contraseña. Haz clic en el siguiente enlace para continuar:</p>
                <p>
                    <a href="{link_recuperacion}"
                       style="background-color: #df8755;
                              color: white;
                              padding: 10px 20px;
                              text-decoration: none;
                              border-radius: 5px;">
                        Restablecer contraseña
                    </a>
                </p>
                <p>Este enlace expirará en 1 hora por seguridad.</p>
                <p>Si no solicitaste este cambio, puedes ignorar este correo.</p>
                <p style="color: #666; font-size: 12px;">Este es un correo automático, por favor no responder.</p>
            </body>
        </html>
        """
        parte_html = MIMEText(html, 'html')
        msg.attach(parte_html)
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)

        return True
    except Exception as e:
        logger.error(f"Error enviando correo: {str(e)}")
        return False

@app.route('/solicitar_recuperacion', methods=['POST'])
def solicitar_recuperacion():
    try:
        metodo = request.form['metodo']
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        if metodo == 'email':
            correo = request.form.get('correo')
            if not correo:
                return jsonify(success=False,
                             message="Por favor, ingresa un correo electrónico válido.")

            cursor.execute("SELECT * FROM usuarios WHERE correo = %s", (correo,))
            if not cursor.fetchone():
                return jsonify(success=False,
                             message="El correo no está registrado en el sistema.")

            token = serializer.dumps(correo, salt='recuperar-password')
            if enviar_correo_recuperacion(correo, token):
                return jsonify(success=True,
                             message="Se han enviado las instrucciones a tu correo.")
            else:
                return jsonify(success=False,
                             message="Error al enviar el correo. Intenta más tarde.")
        else:
            return jsonify(success=False,
                         message="Método de recuperación no válido.")

    except Exception as e:
        logger.error(f"Error en solicitar_recuperacion: {str(e)}")
        return render_template('errorSolicitudes.html')
    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()

@app.route('/restablecer_password/<token>', methods=['GET', 'POST'])
def restablecer_password(token):
    try:
        correo = serializer.loads(token, salt='recuperar-password', max_age=3600)
    except:
        return render_template('error.html', message="El enlace ha expirado o no es válido.")

    if request.method == 'POST':
        try:
            if request.is_json:
                data = request.get_json()
                nueva_password = data.get('nueva_password')
            else:
                nueva_password = request.form['nueva_password']

            regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$')
            if not regex.match(nueva_password):
                return jsonify(success=False, message="La contraseña no cumple con los requisitos de seguridad")

            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)

            cursor.execute("""
                SELECT COUNT(*) as reset_count
                FROM cambios_contrasenia
                WHERE correo = %s
                AND fecha >= NOW() - INTERVAL 24 HOUR
                AND estado = 'exitoso'
            """, (correo,))
            reset_count_result = cursor.fetchone()
            reset_count = reset_count_result['reset_count'] if reset_count_result else 0

            if reset_count >= 3:
                cursor.close()
                connection.close()
                return jsonify(success=False, message="Has alcanzado el límite de cambios de contraseña para hoy.")

            password_hash = bcrypt.hashpw(nueva_password.encode('utf-8'), bcrypt.gensalt())
            connection.start_transaction()

            try:
                cursor.execute("UPDATE usuarios SET contrasenia = %s WHERE correo = %s",
                               (password_hash.decode('utf-8'), correo))

                cursor.execute("""
                    INSERT INTO cambios_contrasenia (correo, fecha, estado)
                    VALUES (%s, NOW(), 'exitoso')
                """, (correo,))

                connection.commit()

                return jsonify(success=True, message="Contraseña actualizada correctamente.")

            except Exception as update_error:
                connection.rollback()
                logger.error(f"Error updating password: {str(update_error)}")
                return jsonify(success=False, message="Error al actualizar la contraseña. Intente nuevamente.")

        except Exception as e:
            logger.error(f"Error en restablecer_password: {str(e)}")
            return jsonify(success=False, message="Error al procesar la solicitud.")

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

    return render_template('restablecer_password.html', token=token)


@app.route('/cambiar_password', methods=['GET', 'POST'])
def cambiar_password():
    if 'id_usuario' not in session:
        return redirect(url_for('logueo'))
    id_usuario = session['id_usuario']
    if request.method == 'POST':
        try:
            if not request.is_json:
                return jsonify({'success': False, 'message': 'Formato de datos inválido'}), 400
            try:
                datos = request.get_json()
            except Exception:
                return jsonify({'success': False, 'message': 'Formato JSON inválido'}), 400
            if 'password_actual' not in datos or 'nueva_password' not in datos:
                return jsonify({'success': False, 'message': 'Datos incompletos'}), 400
            if len(datos['nueva_password']) < 8:
                return jsonify({'success': False, 'message': 'La nueva contraseña debe tener al menos 8 caracteres'}), 400
            if datos['nueva_password'] == datos['password_actual']:
                return jsonify({'success': False, 'message': 'La nueva contraseña no puede ser igual a la actual'}), 400

            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute('SELECT contrasenia FROM usuarios WHERE id_usuarios = %s', (id_usuario,))
            usuario = cursor.fetchone()

            # Verificar la contraseña actual
            if not bcrypt.checkpw(datos['password_actual'].encode('utf-8'), usuario['contrasenia'].encode('utf-8')):
                return jsonify({'success': False, 'message': 'Credenciales inválidas'}), 400

            # Hashear la nueva contraseña
            nueva_password_hashed = bcrypt.hashpw(datos['nueva_password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            cursor.execute(
                'UPDATE usuarios SET contrasenia = %s WHERE id_usuarios = %s',
                (nueva_password_hashed, id_usuario)
            )
            connection.commit()
            return jsonify({'success': True, 'message': 'Contraseña actualizada correctamente'})

        except Exception as e:
            print(f"Error en cambiar_password POST: {e}")
            return jsonify({'success': False, 'message': f'Error al cambiar la contraseña: {str(e)}'}), 500

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    return render_template('cambiar_password.html')

@app.route('/buscar_productos', methods=['GET'])
def buscar_productos():
    try:
        termino_busqueda = request.args.get('termino', '')
        precio_min = request.args.get('precioMin', type=float)
        precio_max = request.args.get('precioMax', type=float)
        marca = request.args.get('marca', '')

        query = """
            SELECT p.id_producto, p.nombre, p.descripcion, p.precio,
                   p.cantidad, p.ubicacion, p.marca, p.color, p.tamano
            FROM productos p
            WHERE 1=1
        """
        params = []

        if termino_busqueda:
            query += " AND p.nombre LIKE %s"
            params.append(f"%{termino_busqueda}%")

        if precio_min is not None:
            query += " AND p.precio >= %s"
            params.append(precio_min)

        if precio_max is not None:
            query += " AND p.precio <= %s"
            params.append(precio_max)

        if marca:
            query += " AND p.marca LIKE %s"
            params.append(f"%{marca}%")

        query += " ORDER BY p.id_producto DESC"

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        productos = cursor.fetchall()

        for producto in productos:
            cursor.execute("""
                SELECT imagen
                FROM imagenes
                WHERE id_producto = %s
                ORDER BY id_imagen
            """, (producto['id_producto'],))

            imagenes = cursor.fetchall()
            producto['imagenes'] = []

            for imagen in imagenes:
                if imagen and imagen['imagen']:
                    try:
                        imagen_base64 = base64.b64encode(imagen['imagen']).decode('utf-8')
                        producto['imagenes'].append(imagen_base64)
                    except Exception as e:
                        print(f"Error al convertir imagen: {e}")
                        continue

        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'productos': productos
        })

    except Exception as e:
        print(f"Error en la búsqueda: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            fecha_nacimiento = request.form['fecha_nacimiento']
            direccion = request.form['direccion']
            telefono = request.form['telefono']
            correo = request.form['correo']
            contrasenia = request.form['password']
            genero = request.form['genero']
            foto_perfil = request.files.get('foto_perfil')

            # Validación de edad
            fecha_nacimiento_dt = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
            edad = (datetime.now() - fecha_nacimiento_dt).days // 365
            if edad < 18:
                return redirect(url_for('registro', menor_de_edad='true'))

            # Validación de correo
            if not correo.endswith('@gmail.com'):
                return redirect(url_for('registro', correo_invalido='true'))

            # Conexión a la base de datos
            connection = get_db_connection()
            cursor = connection.cursor()

            # Verificar si el correo ya existe
            cursor.execute('SELECT COUNT(*) FROM usuarios WHERE correo = %s', (correo,))
            if cursor.fetchone()[0] > 0:
                cursor.close()
                connection.close()
                return redirect(url_for('registro', correo_existente='true'))

            # Hashear la contraseña
            hashed_password = bcrypt.hashpw(contrasenia.encode('utf-8'), bcrypt.gensalt())

            # Manejar la foto de perfil
            try:
                if foto_perfil and foto_perfil.filename != '':
                    # Si se subió una foto, usarla
                    foto_perfil_data = foto_perfil.read()
                else:
                    # Si no se subió foto, usar la imagen por defecto
                    default_image_path = os.path.join(current_app.root_path, 'static', 'SinPerfil.png')
                    if os.path.exists(default_image_path):
                        with open(default_image_path, 'rb') as f:
                            foto_perfil_data = f.read()
                    else:
                        print(f"Error: No se encuentra la imagen por defecto en {default_image_path}")
                        raise FileNotFoundError("No se encuentra la imagen por defecto")

                # Insertar en la base de datos
                query = '''
                    INSERT INTO usuarios (nombre, fecha_nacimiento, genero, direccion,
                                       telefono, correo, contrasenia, foto_perfil)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                '''
                cursor.execute(query, (nombre, fecha_nacimiento, genero, direccion,
                                     telefono, correo, hashed_password, foto_perfil_data))

                connection.commit()

            except Exception as e:
                print(f"Error al procesar la imagen: {str(e)}")
                connection.rollback()
                raise

            finally:
                cursor.close()
                connection.close()

            return redirect(url_for('registro', registro_exitoso='true'))

        except Exception as e:
            print(f"Error en el registro: {str(e)}")
            return redirect(url_for('registro', error='true'))

    return render_template("Registro.html",
                         correo_existente=request.args.get('correo_existente', False),
                         correo_invalido=request.args.get('correo_invalido', False),
                         registro_exitoso=request.args.get('registro_exitoso', False),
                         menor_de_edad=request.args.get('menor_de_edad', False))
@app.route('/mostrar_foto_perfil/<int:usuario_id>')
def mostrar_foto_perfil(usuario_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Recuperar la foto de perfil
    query = 'SELECT foto_perfil FROM usuarios WHERE id = %s'
    cursor.execute(query, (usuario_id,))
    resultado = cursor.fetchone()

    cursor.close()
    connection.close()

    if resultado and resultado[0]:
        # Devolver la imagen original
        return send_file(
            BytesIO(resultado[0]),
            mimetype='image/jpeg',  # Ajuste según el tipo de imagen
            as_attachment=False
        )
    else:
        # Imagen por defecto si no hay foto de perfil
        return send_from_directory('static/images', 'default_profile.jpg')

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
        return redirect(url_for('logueo'))
    id_usuario = session['id_usuario']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos WHERE id_producto = %s AND id_usuarios = %s", (id_producto, id_usuario))
    producto = cursor.fetchone()
    cursor.execute("SELECT imagen FROM imagenes WHERE id_producto = %s", (id_producto,))
    imagenes = cursor.fetchall()
    cursor.close()
    conn.close()
    if producto is None:
        return "No se encontró el producto para este usuario", 404
    return render_template('EditarProducto.html', producto=producto, imagenes=imagenes)

@app.route('/get_product_image/<int:id_producto>')
def get_product_image(id_producto):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT imagen FROM imagenes WHERE id_producto = %s LIMIT 1", (id_producto,))
        imagen = cursor.fetchone()

        if imagen:
            return Response(imagen[0], mimetype='image/png')
        else:
            return 'No se encontró la imagen', 404
    finally:
        cursor.close()
        conn.close()

@app.route('/guardar_producto', methods=['POST'])
def guardar_producto():
    if 'id_usuario' not in session:
        return jsonify({"status": "error", "message": "Usuario no autenticado"}), 403

    datos = request.form.to_dict()
    imagen = request.files.get('imagen')

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
        # Actualizar los datos del producto
        cursor.execute("""
            UPDATE productos
            SET nombre = %s, descripcion = %s, precio = %s, cantidad = %s, tipo_venta = %s,
                ubicacion = %s, marca = %s, color = %s, tamano = %s
            WHERE id_producto = %s AND id_usuarios = %s
        """, (nombre, descripcion, precio, cantidad, tipo_venta, ubicacion, marca, color, tamano, id_producto, session['id_usuario']))

        # Si se envió una nueva imagen, actualizarla en la base de datos
        if imagen:
            imagen_binaria = imagen.read()
            cursor.execute("UPDATE imagenes SET imagen = %s WHERE id_producto = %s", (imagen_binaria, id_producto))

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
        user_id = session.get('id_usuario')
        usuario_info = None
        if user_id:
            cursor.execute("SELECT nombre, foto_perfil FROM usuarios WHERE id_usuarios = %s", (user_id,))
            usuario_info = cursor.fetchone()
            if usuario_info and usuario_info['foto_perfil']:
                usuario_info['foto_perfil'] = base64.b64encode(usuario_info['foto_perfil']).decode('utf-8')

        # Obtener los productos con todas sus propiedades, incluyendo likes
        cursor.execute("""
            SELECT
                p.id_producto,
                p.nombre,
                p.descripcion,
                p.precio,
                p.cantidad,
                p.ubicacion,
                p.marca,
                p.color,
                p.tamano,
                COUNT(DISTINCT l.id_like) as likes_count,
                MAX(CASE WHEN l.id_usuario = %s THEN 1 ELSE 0 END) as is_liked
            FROM productos p
            LEFT JOIN likes l ON p.id_producto = l.id_producto
            GROUP BY p.id_producto, p.nombre, p.descripcion, p.precio,
                     p.cantidad, p.ubicacion, p.marca, p.color, p.tamano
            ORDER BY p.id_producto DESC
        """, (user_id if user_id else None,))

        productos = cursor.fetchall()

        # Para cada producto, obtener sus imágenes
        for producto in productos:
            cursor.execute("""
                SELECT imagen
                FROM imagenes
                WHERE id_producto = %s
                ORDER BY id_imagen
            """, (producto['id_producto'],))

            imagenes = cursor.fetchall()
            producto['imagenes'] = []
            producto['is_liked'] = bool(producto['is_liked'])  # Convertir a booleano

            for imagen in imagenes:
                if imagen and imagen['imagen']:
                    try:
                        imagen_base64 = base64.b64encode(imagen['imagen']).decode('utf-8')
                        producto['imagenes'].append(imagen_base64)
                    except Exception as e:
                        print(f"Error al convertir imagen: {e}")
                        continue

        cursor.close()
        conn.close()

        return render_template('index.html', productos=productos, usuario_info=usuario_info)

    except mysql.connector.Error as err:
        print(f"Error en la base de datos: {err}")
        return f"Error en la base de datos: {err}"
    except Exception as e:
        print(f"Error general: {str(e)}")
        return f"Error general: {str(e)}"

@app.route('/toggle_like/<int:id_producto>', methods=['POST'])
def toggle_like(id_producto):
    if 'id_usuario' not in session:
        return jsonify({'status': 'error', 'message': 'Usuario no autenticado'}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Verificar si el producto existe
        cursor.execute("SELECT id_producto FROM productos WHERE id_producto = %s", (id_producto,))
        if not cursor.fetchone():
            return jsonify({'status': 'error', 'message': 'Producto no encontrado'}), 404

        # Verificar si ya existe el like
        cursor.execute("""
            SELECT id_like
            FROM likes
            WHERE id_producto = %s AND id_usuario = %s
        """, (id_producto, session['id_usuario']))

        existing_like = cursor.fetchone()

        try:
            if existing_like:
                # Eliminar like existente
                cursor.execute("""
                    DELETE FROM likes
                    WHERE id_producto = %s AND id_usuario = %s
                """, (id_producto, session['id_usuario']))
                is_liked = False
            else:
                # Insertar nuevo like
                cursor.execute("""
                    INSERT INTO likes (id_producto, id_usuario)
                    VALUES (%s, %s)
                """, (id_producto, session['id_usuario']))
                is_liked = True

            conn.commit()

            # Obtener el nuevo conteo de likes
            cursor.execute("""
                SELECT COUNT(*) as likes_count
                FROM likes
                WHERE id_producto = %s
            """, (id_producto,))

            likes_count = cursor.fetchone()['likes_count']

        except mysql.connector.Error as err:
            conn.rollback()
            raise err

        finally:
            cursor.close()
            conn.close()

        return jsonify({
            'status': 'success',
            'is_liked': is_liked,
            'likes_count': likes_count
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

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




def allowed_file(filename):
    """Verificar si la extensión del archivo es permitida"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/registrar_producto', methods=['GET', 'POST'])
def registrar_producto():
    if request.method == 'GET':
        return render_template('RegistrarProducto.html')

    if 'id_usuario' not in session:
        return jsonify({'status': 'error', 'message': 'Usuario no autenticado'}), 403

    try:
        # Obtener datos del formulario
        id_usuario = session['id_usuario']
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        precio = request.form.get('precio')
        cantidad = request.form.get('cantidad')
        tipo_venta = request.form.get('tipo_venta')
        ubicacion = request.form.get('ubicacion')
        marca = request.form.get('marca', '')
        color = request.form.get('color', '')
        tamano = request.form.get('tamano', '')

        # Validar campos requeridos
        if not all([nombre, descripcion, precio, cantidad, tipo_venta, ubicacion]):
            return jsonify({
                'status': 'error',
                'message': 'Todos los campos obligatorios deben estar completos'
            }), 400

        # Obtener las imágenes como archivos
        imagenes = request.files.getlist('imagenes')
        if not imagenes:
            return jsonify({
                'status': 'error',
                'message': 'Debe incluir al menos una imagen'
            }), 400

        # Validar formato de imágenes
        for imagen in imagenes:
            if not allowed_file(imagen.filename):
                return jsonify({
                    'status': 'error',
                    'message': 'Formato de imagen no permitido. Use PNG, JPG'
                }), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # Insertar el producto
            producto_query = '''
                INSERT INTO productos (
                    id_usuarios, nombre, descripcion, cantidad,
                    tipo_venta, precio, ubicacion, marca,
                    color, tamano
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            '''
            producto_valores = (
                id_usuario, nombre, descripcion, cantidad,
                tipo_venta, precio, ubicacion, marca,
                color, tamano
            )

            cursor.execute(producto_query, producto_valores)
            id_producto = cursor.lastrowid

            # Procesar y guardar las imágenes (máximo 5)
            for imagen in imagenes[:5]:
                # Leer el archivo de imagen
                imagen_binaria = imagen.read()

                # Insertar la imagen en la base de datos
                imagen_query = '''
                    INSERT INTO imagenes (id_producto, imagen)
                    VALUES (%s, %s)
                '''
                cursor.execute(imagen_query, (id_producto, imagen_binaria))

            connection.commit()
            return jsonify({
                'status': 'success',
                'message': 'Producto registrado exitosamente',
                'id_producto': id_producto
            }), 200

        except mysql.connector.Error as err:
            connection.rollback()
            print(f"Error de MySQL: {err}")
            return jsonify({
                'status': 'error',
                'message': 'Error al guardar en la base de datos'
            }), 500
        finally:
            cursor.close()
            connection.close()

    except Exception as e:
        print(f"Error general: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error al procesar la solicitud'
        }), 500

@app.route('/mis_publicaciones', methods=['GET'])
def mis_publicaciones():
    try:
        if 'id_usuario' not in session:
            return redirect(url_for('logueo'))

        id_usuario = session['id_usuario']
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Consulta del perfil del usuario
        query_usuario = '''
            SELECT nombre, foto_perfil, fecha_nacimiento, direccion, telefono, correo, genero
            FROM usuarios
            WHERE id_usuarios = %s
        '''
        cursor.execute(query_usuario, (id_usuario,))
        usuario = cursor.fetchone()

        if not usuario:
            return "Usuario no encontrado", 404

        # Convertir la foto de perfil de BLOB a base64
        if usuario['foto_perfil']:
            usuario['foto_perfil'] = base64.b64encode(usuario['foto_perfil']).decode('utf-8')
        else:
            usuario['foto_perfil'] = None

        # Consulta para obtener productos
        query_productos = '''
            SELECT id_producto, nombre, descripcion, precio
            FROM productos
            WHERE id_usuarios = %s
        '''
        cursor.execute(query_productos, (id_usuario,))
        productos = cursor.fetchall()

        # Obtener todas las imágenes para cada producto
        for producto in productos:
            query_imagenes = '''
                SELECT imagen
                FROM imagenes
                WHERE id_producto = %s
            '''
            cursor.execute(query_imagenes, (producto['id_producto'],))
            imagenes = cursor.fetchall()

            # Convertir todas las imágenes a base64
            producto['imagenes'] = [
                base64.b64encode(img['imagen']).decode('utf-8')
                for img in imagenes
            ]

        cursor.close()
        connection.close()

        # Si la solicitud es AJAX, devolver solo la lista de publicaciones
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template('partial_publicaciones.html', productos=productos, usuario=usuario)

        # Si no es AJAX, renderizar la página completa
        return render_template('mis_publicaciones.html', productos=productos, usuario=usuario)

    except Exception as e:
        print(f"Error: {e}")
        return "Ocurrió un error en el servidor", 500

@app.route('/carrito', methods=['GET'])
def carrito():
    try:
        if 'id_usuario' not in session:
            return redirect(url_for('logueo'))

        id_usuario = session['id_usuario']
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        productos_carrito = []
        total = 0

        if 'carrito' in session:
            carrito_ids = session['carrito']
            if carrito_ids:
                # Obtener productos con sus imágenes
                query = """
                    SELECT p.*, i.imagen
                    FROM productos p
                    LEFT JOIN imagenes i ON p.id_producto = i.id_producto
                    WHERE p.id_producto IN (%s)
                """ % ','.join(['%s'] * len(carrito_ids))

                cursor.execute(query, tuple(carrito_ids))
                resultado = cursor.fetchall()

                # Procesar los productos y sus imágenes
                productos_temp = {}
                for row in resultado:
                    id_producto = row['id_producto']
                    if id_producto not in productos_temp:
                        productos_temp[id_producto] = {
                            'id_producto': id_producto,
                            'nombre': row['nombre'],
                            'descripcion': row['descripcion'],
                            'precio': float(row['precio']),
                            'cantidad': row['cantidad'],
                            'imagenes': []
                        }
                        total += float(row['precio'])

                    # Agregar imagen si existe
                    if row['imagen'] is not None:
                        try:
                            imagen_base64 = base64.b64encode(row['imagen']).decode('utf-8')
                            productos_temp[id_producto]['imagenes'].append(imagen_base64)
                        except Exception as img_error:
                            print(f"Error procesando imagen: {img_error}")

                # Convertir el diccionario temporal a lista
                productos_carrito = list(productos_temp.values())

        cursor.close()
        connection.close()

        return render_template('carrito.html', productos=productos_carrito, total=total)

    except Exception as e:
        print(f"Error: {e}")
        return "Ocurrió un error en el servidor", 500

@app.context_processor
def cart_counter():
    """
    Función de contexto para contar los productos en el carrito.
    """
    cantidad_carrito = 0
    if 'carrito' in session:
        cantidad_carrito = len(session['carrito'])
    return dict(cantidad_carrito=cantidad_carrito)

@app.route('/agregar_al_carrito', methods=['POST'])
def agregar_al_carrito():
    try:
        if 'id_usuario' not in session:
            return jsonify({"success": False, "message": "Usuario no autenticado"}), 401

        # Obtener el id del producto de la solicitud JSON
        product_id = request.json.get('id_producto')
        if not product_id:
            return jsonify({"success": False, "message": "Producto no especificado"}), 400

        # Agregar el producto al carrito en la sesión
        if 'carrito' not in session:
            session['carrito'] = []

        session['carrito'].append(product_id)
        session.modified = True

        return jsonify({"success": True, "message": "Producto añadido al carrito"})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": "Error en el servidor"}), 500

@app.route('/guardar_carrito', methods=['POST'])
def guardar_carrito():
    try:
        if 'id_usuario' not in session:
            return jsonify({"success": False, "message": "Usuario no autenticado"}), 401

        id_usuario = session['id_usuario']
        carrito = request.json.get("carrito", [])

        if not carrito:
            return jsonify({"success": True, "message": "Carrito vacío guardado"}), 200

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # Iniciar transacción
            connection.start_transaction()

            # Eliminar entradas existentes
            cursor.execute("DELETE FROM carritos WHERE id_usuario = %s", (id_usuario,))

            # Insertar nuevos productos
            for producto in carrito:
                id_producto = producto['id']
                cantidad = producto.get('cantidad', 1)
                cursor.execute(
                    "INSERT INTO carritos (id_usuario, id_producto, cantidad) VALUES (%s, %s, %s)",
                    (id_usuario, id_producto, cantidad)
                )

            # Confirmar transacción
            connection.commit()

            # Actualizar sesión
            session['carrito'] = [producto['id'] for producto in carrito]
            session.modified = True

        except mysql.connector.Error as db_error:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

        return jsonify({"success": True, "message": "Carrito guardado exitosamente"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": f"Error en el servidor: {str(e)}"}), 500

@app.route('/eliminar_producto_carrito', methods=['POST'])
def eliminar_producto_carrito():
    try:
        if 'id_usuario' not in session:
            return jsonify({"success": False, "message": "Usuario no autenticado"}), 401

        id_usuario = session['id_usuario']
        id_producto = request.json.get('id_producto')

        if not id_producto:
            return jsonify({"success": False, "message": "ID de producto no proporcionado"}), 400

        # Conectar a la base de datos
        connection = get_db_connection()
        cursor = connection.cursor()

        # Eliminar el producto del carrito del usuario
        cursor.execute(
            "DELETE FROM carritos WHERE id_usuario = %s AND id_producto = %s",
            (id_usuario, id_producto)
        )
        connection.commit()

        # Actualizar el carrito en la sesión del servidor
        if 'carrito' in session:
            session['carrito'] = [p for p in session['carrito'] if p != id_producto]
            session.modified = True

        cursor.close()
        connection.close()

        return jsonify({"success": True, "message": "Producto eliminado del carrito"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": "Error en el servidor"}), 500


@app.route('/pagos', methods=['GET'])
def pagos():
    try:
        # Verificar si el usuario está en sesión
        if 'id_usuario' not in session:
            return redirect(url_for('logueo'))

        # Renderizar la plantilla de "Formas de Pago"
        return render_template('pagos.html')

    except Exception as e:
        print(f"Error: {e}")
        return "Ocurrió un error en el servidor", 500

@app.route('/ver_perfil')
def ver_perfil():
    if 'id_usuario' not in session:
        return redirect(url_for('logueo'))

    return redirect(url_for('ver_perfil_usuario', user_id=session['id_usuario']))

@app.route('/edicionUsr', methods=['GET', 'POST'])
def edicionUsr():
    if 'id_usuario' not in session:
        return redirect(url_for('logueo'))

    id_usuario = session['id_usuario']

    # Manejar la solicitud POST (actualización de datos)
    if request.method == 'POST':
        try:
            # Verificar si la solicitud contiene datos JSON o form-data
            if request.is_json:
                datos = request.get_json()

                # Validar que existan todos los campos requeridos
                if not all(key in datos for key in ['nombre','fecha_nacimiento', 'direccion', 'correo', 'telefono', 'genero']):
                    return jsonify({'success': False, 'message': 'Faltan datos requeridos'}), 400

                # Validar el formato del correo
                if not datos['correo'].endswith('@gmail.com'):
                    return jsonify({'success': False, 'message': 'El correo debe ser un Gmail válido'}), 400

                # Validar la edad
                fecha_nacimiento = datetime.strptime(datos['fecha_nacimiento'], '%Y-%m-%d')
                edad = (datetime.now() - fecha_nacimiento).days / 365.25
                if edad < 18:
                    return jsonify({'success': False, 'message': 'Debe ser mayor de 18 años'}), 400

                # Conectar y actualizar la base de datos
                connection = get_db_connection()
                cursor = connection.cursor()

                query = '''
                    UPDATE usuarios
                    SET nombre = %s,
                        fecha_nacimiento = %s,
                        direccion = %s,
                        correo = %s,
                        telefono = %s,
                        genero = %s
                    WHERE id_usuarios = %s
                '''

                cursor.execute(query, (
                    datos['nombre'],
                    datos['fecha_nacimiento'],
                    datos['direccion'],
                    datos['correo'],
                    datos['telefono'],
                    datos['genero'],
                    id_usuario
                ))

                connection.commit()
                cursor.close()
                connection.close()

                return jsonify({
                    'success': True,
                    'message': 'Datos actualizados correctamente'
                })
            else:
                if 'foto_perfil' not in request.files:
                    return jsonify({'success': False, 'message': 'No se recibió ninguna imagen'}), 400

                foto_perfil = request.files['foto_perfil']

                if foto_perfil.filename == '':
                    return jsonify({'success': False, 'message': 'No se seleccionó ningún archivo'}), 400

                try:
                    image = Image.open(foto_perfil)
                    image = image.convert("RGB")

                    if image.width > 180 or image.height > 180:
                        return jsonify({'success': False, 'message': 'La imagen debe ser de máximo 180x180 píxeles'}), 400

                    img_io = BytesIO()
                    image.save(img_io, format='JPEG')
                    foto_perfil_data = img_io.getvalue()

                    connection = get_db_connection()
                    cursor = connection.cursor()

                    query = '''
                        UPDATE usuarios
                        SET foto_perfil = %s
                        WHERE id_usuarios = %s
                    '''

                    cursor.execute(query, (foto_perfil_data, id_usuario))
                    connection.commit()
                    cursor.close()
                    connection.close()

                    return jsonify({
                        'success': True,
                        'message': 'Foto de perfil actualizada correctamente'
                    })

                except Exception as e:
                    return jsonify({
                        'success': False,
                        'message': f'Error al procesar la imagen: {str(e)}'
                    }), 500

        except Exception as e:
            print(f"Error en edicionUsr POST: {e}")
            return jsonify({
                'success': False,
                'message': f'Error al actualizar los datos: {str(e)}'
            }), 500

    else:
        try:
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

            if datos_usuario is None:
                return "No se encontró el usuario", 404

            if datos_usuario['fecha_nacimiento']:
                datos_usuario['fecha_nacimiento'] = datos_usuario['fecha_nacimiento'].strftime('%Y-%m-%d')

            return render_template('edicionUsr.html', datos_usuario=datos_usuario)

        except Exception as e:
            print(f"Error en edicionUsr GET: {e}")
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


@app.route('/eliminarCuenta', methods=['POST'])
def eliminarCuenta():
    if 'id_usuario' not in session:
        return redirect(url_for('logueo'))

    id_usuario = session['id_usuario']

    try:
        # Conectar a la base de datos y eliminar el usuario
        connection = get_db_connection()
        cursor = connection.cursor()

        # Consulta para eliminar la cuenta del usuario
        query = 'DELETE FROM usuarios WHERE id_usuarios = %s'
        cursor.execute(query, (id_usuario,))

        connection.commit()
        cursor.close()
        connection.close()

        # Limpiar la sesión después de eliminar la cuenta
        session.pop('id_usuario', None)

        return jsonify({
            'success': True,
            'message': 'Cuenta eliminada correctamente'
        })

    except Exception as e:
        print(f"Error al eliminar la cuenta: {e}")
        return jsonify({
            'success': False,
            'message': f'Error al eliminar la cuenta: {str(e)}'
        }), 500

@app.route('/ConfirmarCompra/<int:user_id>')
def confirmar_compra(user_id):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Consulta para obtener datos del usuario
        query_usuario = '''
            SELECT nombre, direccion, telefono, correo, foto_perfil
            FROM usuarios
            WHERE id_usuarios = %s
        '''
        cursor.execute(query_usuario, (user_id,))
        datos_usuario = cursor.fetchone()

        # Verificar si el usuario existe
        if not datos_usuario:
            return render_template('error.html', message='Usuario no encontrado'), 404

        # Consulta para obtener productos en el carrito
        query_carrito = '''
            SELECT
                p.nombre AS nombre_producto,
                p.precio AS precio,
                c.cantidad AS cantidad,
                (p.precio * c.cantidad) AS subtotal
            FROM carritos c
            INNER JOIN productos p ON c.id_producto = p.id_producto
            WHERE c.id_usuario = %s
        '''

        try:
            cursor.execute(query_carrito, (user_id,))
            productos_carrito = cursor.fetchall()

            if not productos_carrito:
                productos_carrito = []  # Si no hay productos, inicializamos una lista vacía

            # Calcular el total de la compra de manera segura
            total_compra = 0
            for producto in productos_carrito:
                if producto['subtotal'] is not None:
                    total_compra += float(producto['subtotal'])

            monto_pagar = total_compra + 50

            # Imprimir información de depuración
            print(f"Productos encontrados: {len(productos_carrito)}")
            print(f"Total calculado: {total_compra}")

        except Exception as e:
            print(f"Error en la consulta del carrito: {str(e)}")
            productos_carrito = []
            total_compra = 0

        # Consulta para obtener el último método de pago
        query_pago = '''
            SELECT metodo_pago
            FROM pagos
            WHERE id_usuario = %s
            ORDER BY id_pago DESC
            LIMIT 1
        '''

        try:
            cursor.execute(query_pago, (user_id,))
            ultimo_pago = cursor.fetchone()
            metodo_pago = ultimo_pago['metodo_pago'] if ultimo_pago else 'No registrado'

        except Exception as e:
            print(f"Error en la consulta del método de pago: {str(e)}")
            metodo_pago = 'No registrado'

        # Preparar datos para la plantilla
        datos_compra = {
            'productos': productos_carrito,
            'total': total_compra,
            'monto_pagar': monto_pagar,
            'metodo_pago': metodo_pago  # Incluir el método de pago en los datos
        }

        is_owner = 'id_usuario' in session and session['id_usuario'] == user_id

        # Imprimir información de depuración antes de renderizar
        print(f"Datos de usuario: {datos_usuario}")
        print(f"Datos de compra: {datos_compra}")

        return render_template('ConfirmarCompra.html',
                               datos_usuario=datos_usuario,
                               datos_compra=datos_compra,
                               is_owner=is_owner)

    except Exception as e:
        print(f"Error general en confirmar_compra: {str(e)}")
        return render_template('error.html', message='Error al procesar la solicitud'), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@app.route('/guardar_pago', methods=['POST'])
def guardar_pago():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No se recibieron datos'}), 400

        id_usuario = data.get('id_usuario')
        metodo_pago = data.get('metodo_pago')
        num_transaccion = data.get('num_transaccion')

        if not id_usuario or not metodo_pago:
            return jsonify({'success': False, 'message': 'Datos incompletos'}), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        query = '''
            INSERT INTO pagos (id_usuario, metodo_pago, num_transaccion)
            VALUES (%s, %s, %s)
        '''
        cursor.execute(query, (id_usuario, metodo_pago, num_transaccion))
        connection.commit()

        return jsonify({
            'success': True,
            'message': 'Pago registrado exitosamente',
            'redirect_url': f'/ConfirmarCompra/{id_usuario}'
        }), 200

    except Exception as e:
        print(f"Error in guardar_pago: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)

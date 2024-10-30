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

def get_db_connection():
    """Establece la conexión a la base de datos."""
    return mysql.connector.connect(**db_config)

# Ruta para la página de inicio de sesión
@app.route('/')
def logueo():
    return render_template('Logueo.html')


@app.route('/ver_perfil/<int:user_id>')
def ver_perfil_usuario(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = '''
        SELECT nombre, fecha_nacimiento, genero, direccion, telefono, correo
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


@app.route('/producto/<int:id_producto>', methods=['GET'])
def obtener_producto(id_producto):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*, u.nombre as nombre_usuario, u.id_usuarios as id_vendedor 
        FROM productos p 
        JOIN usuarios u ON p.id_usuarios = u.id_usuarios 
        WHERE p.id_producto = %s
    """, (id_producto,))
    producto = cursor.fetchone()
    cursor.close()
    conn.close()

    if producto:
        return jsonify(producto)
    else:
        return jsonify({'error': 'Producto no encontrado'}), 404

@app.route('/ver_perfil')
def ver_perfil():
    if 'id_usuario' not in session:
        return redirect(url_for('logueo'))
    
    return redirect(url_for('ver_perfil_usuario', user_id=session['id_usuario']))
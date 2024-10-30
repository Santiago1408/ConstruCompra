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
@app.route('/ver_perfil')
def ver_perfil():
    if 'id_usuario' not in session:
        return redirect(url_for('logueo'))

    # Obtener el ID del usuario de la sesión
    id_usuario = session['id_usuario']

    # Consultar los datos del usuario
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

    # Pasar los datos del usuario al HTML 'ver_perfil.html'
    return render_template('ver_perfil.html', datos_usuario=datos_usuario)

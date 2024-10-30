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

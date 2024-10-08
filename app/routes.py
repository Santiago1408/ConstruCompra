from flask import Blueprint, render_template, request, redirect, url_for, send_file, flash
from app import db
from app.models import Producto  
from app.utils import save_image

bp = Blueprint('main', __name__)

@bp.route('/create_producto')
def create_producto():
    return render_template('create_producto.html')


@bp.route('/cargar_producto', methods=['POST'])  # Cambiado el nombre de la ruta
def cargar_producto():
    nombre = request.form['nombre']
    id_usuarios = 1  #id del usuario mientras 1 
    descripcion = request.form.get('descripcion')  #Campo opcional
    cantidad = request.form.get('cantidad', 0)  # Campo opcional, con valor por defecto 0
    tipo_venta = request.form['tipo_venta']  #'Unitario' o 'Total'
    precio = request.form['precio']
    ubicacion = request.form['ubicacion']
    marca = request.form.get('marca')  # Campo opcional
    color = request.form.get('color')  # Campo opcional
    tamano = request.form.get('tamano')  # Campo opcional
    #imagen = request.files['imagen']  # Si la imagen es requerida

    # Procesar la imagen si es necesario
    #img_data = save_image(imagen)  # Esto guarda la imagen en tu sistema

    # Crear una instancia del producto con los datos capturados
    producto = Producto(
        id_usuarios=id_usuarios,
        nombre=nombre,
        descripcion=descripcion,
        cantidad=cantidad,
        tipo_venta=tipo_venta,
        precio=precio,
        ubicacion=ubicacion,
        marca=marca,
        color=color,
        tamano=tamano,
        #imagen=img_data 
    )
    
    # Guardar el producto en la base de datos
    db.session.add(producto)
    db.session.commit()
    flash('Producto registrado exitosamente', 'success')
    return redirect(url_for('main.create_producto'))
    # return redirect(url_for('main.index'))

@bp.route('/')
def index():
    productos = Producto.query.all() 
    return render_template('index.html', productos=productos) 

@bp.route('/producto/<int:id_producto>/imagen') 
def obtener_imagen(id_producto):
    producto = Producto.query.get(id_producto) 
    if producto and producto.imagen:
        return send_file(io.BytesIO(producto.imagen), mimetype='image/jpeg')
    return "Imagen no encontrada", 404

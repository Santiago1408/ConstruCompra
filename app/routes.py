from flask import Blueprint, render_template, request, redirect, url_for, send_file
from app import db
from app.models import Producto  
from app.utils import save_image

bp = Blueprint('main', __name__)

@bp.route('/cargar_producto', methods=['POST'])  # Cambiado el nombre de la ruta
def cargar_producto():
    nombre = request.form['nombre']
    precio = request.form['precio']
    descripcion = request.form['descripcion']
    imagen = request.files['imagen']

    img_data = save_image(imagen)

    producto = Producto(nombre=nombre, precio=precio, descripcion=descripcion, imagen=img_data)  
    db.session.add(producto)
    db.session.commit()
    return redirect(url_for('main.index'))

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

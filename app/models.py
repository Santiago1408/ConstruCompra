from app import db

class Producto(db.Model):
    __tablename__ = 'productos'  

    id_producto = db.Column(db.Integer, primary_key=True)  
    id_usuarios = db.Column(db.Integer, nullable=False)  
    nombre = db.Column(db.String(25), nullable=False)  
    descripcion = db.Column(db.String(100))  
    cantidad = db.Column(db.Integer)  
    tipo_venta = db.Column(db.Enum('Unitario', 'Total'), nullable=False) 
    precio = db.Column(db.Numeric(10, 2), nullable=False)  
    ubicacion = db.Column(db.String(255), nullable=False) 
    marca = db.Column(db.String(50))  
    color = db.Column(db.String(50))  
    tamano = db.Column(db.String(50))  
    fecha_publicacion = db.Column(db.DateTime, default=db.func.current_timestamp()) 

    def __repr__(self):
        return f'<Producto {self.nombre}>'


class Usuario(db.Model):
    __tablename__ = 'usuarios' 

    id_usuario = db.Column(db.Integer, primary_key=True)  
    nombre = db.Column(db.String(50), nullable=False)  
    apellido = db.Column(db.String(50), nullable=False)  
    email = db.Column(db.String(100), unique=True, nullable=False)  
    contraseña = db.Column(db.String(100), nullable=False)  
    telefono = db.Column(db.String(15))  
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp())  
    direccion = db.Column(db.String(255))  
    es_admin = db.Column(db.Boolean, default=False) 

    def __repr__(self):
        return f'<Usuario {self.nombre} {self.apellido}>'
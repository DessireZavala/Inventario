from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Modelo para el Producto
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    cantidad = db.Column(db.Integer, default=0)
    imagen_url = db.Column(db.String(200))  # URL de la imagen

# Modelo para el Usuario (con rol)
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    rol = db.Column(db.String(50))  # 'superadmin', 'admin', 'usuario'
    contrasena = db.Column(db.String(100))

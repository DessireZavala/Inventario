# app.py

from flask_login import login_required
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
import os

# Importamos los modelos (Producto, Usuario) desde models.py
from models import db, Producto, Usuario

# Crear una instancia de la aplicación Flask
app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:/Inventario/instance/inventario.db'  # Ruta absoluta correcta
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuración para la carga de imágenes
app.config['UPLOAD_FOLDER'] = 'static/images'  # Directorio donde se guardarán las imágenes
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Tipos de archivo permitidos

# Verificar si el directorio de imágenes existe, si no, crearlo
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Inicialización de la base de datos y Flask-Migrate
db.init_app(app)  # Inicializa la base de datos
migrate = Migrate(app, db)  # Inicializa la migración

# Ruta de inicio (dashboard)
@app.route('/')
@login_required
def index():
    productos = Producto.query.filter_by(cantidad=0).all()
    return render_template('index.html', productos=productos)

# Función para verificar si un archivo tiene una extensión permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Ruta para agregar productos
@app.route('/agregar_producto', methods=['GET', 'POST'])
@login_required
def agregar_producto():
    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre = request.form['nombre']
        cantidad = request.form['cantidad']
        categoria = request.form['categoria']  # Obtener la categoría seleccionada
        imagen = request.files['imagen']

        # Verificar si el archivo tiene una extensión válida
        if imagen and allowed_file(imagen.filename):
            # Guardar el archivo con un nombre seguro
            filename = secure_filename(imagen.filename)
            imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Guardar la imagen en el servidor

            # Crear un nuevo producto y agregarlo a la base de datos
            nuevo_producto = Producto(nombre=nombre, cantidad=cantidad, categoria=categoria, imagen_url=filename)
            db.session.add(nuevo_producto)
            db.session.commit()

            return redirect(url_for('index'))  # Redirigir al índice después de agregar el producto

    return render_template('agregar_producto.html')

if __name__ == '__main__':
    app.run(debug=True)

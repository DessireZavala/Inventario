from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import os
from werkzeug.utils import secure_filename
from flask_migrate import Migrate  # Importación de Flask-Migrate

# Crear la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecreto'  # Clave secreta para proteger sesiones y formularios
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:/Inventario/instance/inventario.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Ruta donde se guardarán las imágenes
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Extensiones permitidas

# Inicializar las extensiones
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Especifica qué vista se debe redirigir si no estás logueado

# Inicializar Flask-Migrate
migrate = Migrate(app, db)  # Esto es lo que agrega la funcionalidad de migraciones

# Modelo de Usuario (adaptado según la estructura de tu tabla)
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), unique=True, nullable=False)
    contrasena = db.Column(db.String(150), nullable=False)
    rol = db.Column(db.String(50), nullable=False)  # Nuevo campo para el rol

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    imagen_url = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)  # Nueva columna de categoría

# Configurar la carga del usuario para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Ruta de inicio (dashboard)
@app.route('/')
@login_required
def index():
    categoria = request.args.get('categoria')  # Obtener el parámetro de la categoría
    
    # Si hay categoría, filtrar los productos por categoría
    if categoria:
        productos = Producto.query.filter(Producto.categoria == categoria, Producto.cantidad > 0).all()
    else:
        # Mostrar todos los productos con cantidad mayor a 0 si no se selecciona ninguna categoría
        productos = Producto.query.filter(Producto.cantidad > 0).all()
    
    # Filtrar productos con cantidad igual a 0 para la sección de "sin stock"
    productos_out_of_stock = Producto.query.filter_by(cantidad=0).all()
    
    return render_template('index.html', productos=productos, productos_out_of_stock=productos_out_of_stock, categoria=categoria)

# Ruta para agregar productos
@app.route('/agregar_producto', methods=['GET', 'POST'])
@login_required
def agregar_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']  # Obtener el nombre del producto
        cantidad = request.form['cantidad']  # Obtener la cantidad
        imagen = request.files['imagen']  # Obtener el archivo de imagen
        categoria = request.form['categoria']  # Obtener la categoría del producto

        if nombre and cantidad and imagen and categoria:
            # Verificar si el archivo tiene una extensión válida
            if imagen and allowed_file(imagen.filename):
                filename = secure_filename(imagen.filename)
                imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Guardar la imagen

                # Crear un nuevo producto con la categoría seleccionada
                nuevo_producto = Producto(nombre=nombre, cantidad=int(cantidad), imagen_url=filename, categoria=categoria)
                db.session.add(nuevo_producto)  # Añadir el producto a la base de datos
                db.session.commit()  # Confirmar los cambios

                flash('Producto agregado exitosamente', 'success')
                return redirect(url_for('index'))  # Redirigir al índice después de agregar
            else:
                flash('La imagen debe tener una extensión válida (png, jpg, jpeg, gif)', 'danger')
        else:
            flash('Por favor, complete todos los campos del formulario', 'danger')

    return render_template('agregar_producto.html')

# Ruta para surtir productos
@app.route('/surtir_producto')
@login_required
def surtir_producto():
    return render_template('surtir_producto.html')  # Aún no tienes esta página, pero la ruta está definida

# Ruta para actualizar la cantidad de productos
@app.route('/update_quantity', methods=['POST'])
@login_required
def update_quantity():
    product_id = request.form['producto_id']  # Obtener el id del producto
    action = request.form['action']  # Obtener la acción (+ o -)

    # Buscar el producto por ID
    producto = Producto.query.get(product_id)

    if producto:
        if action == 'incrementar':
            producto.cantidad += 1  # Incrementar la cantidad
        elif action == 'decrementar' and producto.cantidad > 0:
            producto.cantidad -= 1  # Decrementar la cantidad

        db.session.commit()  # Guardar los cambios en la base de datos
        flash('Cantidad actualizada con éxito', 'success')
    else:
        flash('Producto no encontrado', 'danger')

    return redirect(url_for('index'))  # Redirigir al índice después de la actualización

# Función para verificar si el archivo tiene una extensión permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Inicializar la aplicación
if __name__ == '__main__':
    app.run(debug=True)

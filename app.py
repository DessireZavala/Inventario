from flask_login import login_required
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import os
from werkzeug.utils import secure_filename

# Crear la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecreto'  # Clave secreta para proteger sesiones y formularios
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:/Inventario/instance/inventario.db'
#RUTAS RUTAS RUTAS RUTAS RUTAS
# Dess      'sqlite:///D:/Inventario/instance/inventario.db'
# Vic       'sqlite:///C:/Users/victor jireh/Desktop/Inventario/instance/inventario.db'  # Ruta de la base de datos
# Hannya    
# Hurtado   
# Yovis     
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Configuración para la carga de imágenes
app.config['UPLOAD_FOLDER'] = 'static/images'  # Directorio donde se guardarán las imágenes
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Tipos de archivo permitidos

# Inicializar las extensiones
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Especifica qué vista se debe redirigir si no estás logueado

# Modelo de Usuario (adaptado según la estructura de tu tabla)
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), unique=True, nullable=False)  # Usamos 'nombre' como username
    contrasena = db.Column(db.String(150), nullable=False)  # Usamos 'contrasena' para la password

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    imagen_url = db.Column(db.String(200), nullable=False)

# Configurar la carga del usuario para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Ruta de inicio (dashboard)
@app.route('/')
@login_required
def index():
    productos = Producto.query.filter_by(cantidad=0).all()  # Filtramos productos con cantidad 0
    return render_template('index.html', productos=productos)

# Ruta de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form['nombre']
        contrasena = request.form['contrasena']
        user = Usuario.query.filter_by(nombre=nombre).first()  # Filtrar por 'nombre' en vez de 'username'
        
        if user and bcrypt.check_password_hash(user.contrasena, contrasena):  # Verificar la contraseña
            login_user(user)
            return redirect(url_for('index'))  # Redirigir al dashboard si el login es exitoso
        else:
            flash('Usuario o contraseña incorrectos', 'danger')  # Mostrar mensaje de error

    return render_template('login.html')  # Si es GET, mostrar el formulario de login

# Ruta de logout
@app.route('/logout')
@login_required
def logout():
    logout_user()  # Cerrar sesión
    return redirect(url_for('login'))  # Redirigir al login

# Ruta para agregar productos
@app.route('/agregar_producto', methods=['GET', 'POST'])
@login_required
def agregar_producto():
    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre = request.form['nombre']
        cantidad = request.form['cantidad']
        imagen = request.files['imagen']

    if nombre and cantidad and imagen:
        # Verificar si el archivo tiene una extensión válida
        if imagen and allowed_file(imagen.filename):
            filename = secure_filename(imagen.filename)
            imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Crear un nuevo producto y agregarlo a la base de datos
            nuevo_producto = Producto(nombre=nombre, cantidad=cantidad, imagen_url=filename)
            db.session.add(nuevo_producto)
            db.session.commit()

            return redirect(url_for('index'))

        else:
            flash('La imagen debe tener una extensión válida (png, jpg, jpeg, gif)', 'danger')
    else:
        flash('Por favor, complete todos los campos del formulario', 'danger')

    return render_template('agregar_producto.html')

# Otros endpoints, como login, etc.
if __name__ == '__main__':
    app.run(debug=True)

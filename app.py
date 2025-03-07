from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import os
from werkzeug.utils import secure_filename
from flask_migrate import Migrate

# Crear la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecreto'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:/Inventario/instance/inventario.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Inicializar las extensiones
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Inicializar Flask-Migrate
migrate = Migrate(app, db)

# Modelo de Usuario
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), unique=True, nullable=False)
    contrasena = db.Column(db.String(150), nullable=False)
    rol = db.Column(db.String(50), nullable=False)

# Modelo de Producto
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    imagen_url = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)

# Cargar usuario para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    categoria = request.args.get('categoria')
    
    if categoria:
        productos = Producto.query.filter(Producto.categoria == categoria, Producto.cantidad > 0).all()
    else:
        productos = Producto.query.filter(Producto.cantidad > 0).all()
    
    productos_out_of_stock = Producto.query.filter_by(cantidad=0).all()

    return render_template('index.html', productos=productos, productos_out_of_stock=productos_out_of_stock, categoria=categoria)

@app.route('/agregar_producto', methods=['GET', 'POST'])
@login_required
def agregar_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        cantidad = request.form['cantidad']
        imagen = request.files['imagen']
        categoria = request.form['categoria']

        if nombre and cantidad and imagen and categoria:
            if imagen and allowed_file(imagen.filename):
                filename = secure_filename(imagen.filename)
                imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                nuevo_producto = Producto(nombre=nombre, cantidad=int(cantidad), imagen_url=filename, categoria=categoria)
                db.session.add(nuevo_producto)
                db.session.commit()

                flash('Producto agregado exitosamente', 'success')
                return redirect(url_for('index'))
            else:
                flash('La imagen debe tener una extensión válida', 'danger')
        else:
            flash('Por favor complete todos los campos', 'danger')

    return render_template('agregar_producto.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form['nombre']  # Cambié 'rol' por 'nombre'
        contrasena = request.form['contrasena']
        usuario = Usuario.query.filter_by(nombre=nombre).first()  # Ahora busca por 'nombre'

        if usuario and bcrypt.check_password_hash(usuario.contrasena, contrasena):
            login_user(usuario)
            flash('Ingreso exitoso', 'success')
            return redirect(url_for('index'))

        flash('Nombre o contraseña incorrectos', 'danger')

    return render_template('login.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user,current_user
import os
from werkzeug.utils import secure_filename
from flask_migrate import Migrate


# Crear la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecreto'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/victor jireh/Desktop/Inventario/instance/inventario.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['SESSION_PERMANENT'] = False  # Para que la sesión no dure más allá de la navegación actual
app.config['SESSION_TYPE'] = 'filesystem'  # O puedes usar otros tipos si prefieres

#RUTAS RUTAS RUTAS RUTAS RUTAS
# Dess      'sqlite:///D:/Inventario/instance/inventario.db'
# Vic       'sqlite:///C:/Users/victor jireh/Desktop/Inventario/instance/inventario.db'  # Ruta de la base de datos
# Hannya    
# Hurtado   
# Yovis     

# Inicializar las extensiones
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'  # Mensaje que se muestra si no hay sesión

# Inicializar Flask-Migrate
migrate = Migrate(app, db)


@app.after_request
def no_cache(response):
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Cargar usuario para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))  # Esto carga al usuario desde la base de datos por su ID


# Modelo de Usuario
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), unique=True, nullable=False)
    contrasena = db.Column(db.String(150), nullable=False)
    rol = db.Column(db.String(50), nullable=False)

    def get_id(self):
        return str(self.id)  # Debe devolver un string

# Modelo de Producto
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    imagen_url = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        rol = request.form['nombre']  # Cambié 'rol' por 'nombre'
        contrasena = request.form['contrasena']
        usuario = Usuario.query.filter_by(rol=rol).first()  # Ahora busca por 'nombre'

        if usuario and bcrypt.check_password_hash(usuario.contrasena, contrasena):
            login_user(usuario)
            flash('Ingreso exitoso', 'success')
            return redirect(url_for('index'))

        flash('Nombre o contraseña incorrectos', 'danger')

    return render_template('login.html')

# Ruta de logout
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    session.clear()  # Limpia todos los datos en la sesión
    logout_user()  # Cerrar sesión
    return '', 204  # Respuesta vacía y código 200 para indicar que la sesión se cerró correctamente


############## QUE ES ESTO???? PORqUE es QUE ES NECESARIO O_o
@app.route('/update_quantity', methods=['POST'])
@login_required
def update_quantity():
    producto_id = request.form.get('producto_id')
    nueva_cantidad = request.form.get('cantidad')

    if producto_id and nueva_cantidad:
        producto = Producto.query.get(producto_id)
        if producto:
            producto.cantidad = int(nueva_cantidad)
            db.session.commit()
            flash('Cantidad actualizada exitosamente', 'success')
        else:
            flash('Producto no encontrado', 'danger')
    else:
        flash('Por favor ingrese todos los datos', 'danger')

    return redirect(url_for('index'))



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


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

if __name__ == '__main__':
    app.run(debug=True)

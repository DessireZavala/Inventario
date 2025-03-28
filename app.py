from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from werkzeug.utils import secure_filename
from flask_migrate import Migrate

# Crear la aplicación Flask
app = Flask(__name__)

# Configuración de la clave secreta y la sesión originleeeeeee
app.config['SECRET_KEY'] = 'supersecreto'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:/Inventario/instance/inventario.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['SESSION_PERMANENT'] = False  # Para que la sesión no dure más allá de la navegación actual
app.config['SESSION_TYPE'] = 'filesystem'  # O puedes usar otros tipos si prefieres
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  

#RUTAS RUTAS RUTAS RUTAS RUTAS
# Dess      'sqlite:///D:/Inventario/instance/inventario.db'
# Vic       'sqlite:///C:/Users/victor jireh/Desktop/Inventario/instance/inventario.db'  # Ruta de la base de datos
# Hannya    'sqlite:///C:/Users/hanny/OneDrive/Documents/Inventario - copia/instance/inventario.db'
# Hurtado   
# Yovis     

# Inicializar las extensiones
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Inicializar Flask-Migrate
migrate = Migrate(app, db)

# Para evitar el cache de la sesión
@app.after_request
def no_cache(response):
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.before_request
def before_request():
    session.permanent = True

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

# Ruta para actualizar un producto
@app.route('/update_product', methods=['POST'])
@login_required
def update_product():
    producto_id = request.form['producto_id']
    producto = Producto.query.get(producto_id)

    if producto:
        producto.nombre = request.form['nombre']
        producto.cantidad = int(request.form['cantidad'])
        producto.categoria = request.form['categoria']

        # Manejo de imagen subida
        if 'imagen' in request.files:
            imagen = request.files['imagen']
            if imagen and allowed_file(imagen.filename):
                filename = secure_filename(imagen.filename)
                imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                producto.imagen_url = filename

        db.session.commit()
        flash('Producto actualizado correctamente', 'success')
    
    return redirect(url_for('index'))


# Ruta para eliminar un producto
@app.route('/eliminar_producto/<int:producto_id>', methods=['GET'])
@login_required
def eliminar_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado exitosamente', 'success')
    return redirect(url_for('index'))


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
    return redirect(url_for('login'))


@app.route('/update_quantity', methods=['POST'])
@login_required
def update_quantity():
    producto_id = request.form.get('producto_id')
    action = request.form.get('action')
    cantidad = request.form.get('cantidad')

    producto = Producto.query.get(producto_id)
    if producto:
        if action == 'incrementar':
            if cantidad:
                producto.cantidad += int(cantidad)
            else:
                producto.cantidad += 1
        elif action == 'decrementar' and producto.cantidad > 0:
            producto.cantidad -= 1

        if producto.cantidad == 0:
            # Mover el producto a la lista de sin stock
            db.session.commit()
            flash(f'{producto.nombre} ahora está fuera de stock', 'info')
        elif producto.cantidad > 0:
            db.session.commit()
            flash('Cantidad actualizada exitosamente', 'success')
        else:
            db.session.commit()
            flash(f'{producto.nombre} ha vuelto a estar en stock', 'success')

    return redirect(url_for('index'))


@app.route('/', methods=['GET'])
@login_required
def index():
    query = request.args.get('query')  # Obtener el término de búsqueda desde la URL
    categoria = request.args.get('categoria')  # Obtener la categoría si se pasa

    if query:  # Si hay un término de búsqueda, filtrar productos por nombre
        productos = Producto.query.filter(Producto.nombre.ilike(f'%{query}%')).all()
    elif categoria:  # Si hay una categoría seleccionada, filtrar por categoría
        productos = Producto.query.filter(Producto.categoria == categoria, Producto.cantidad > 0).all()
    else:  # Si no hay búsqueda ni categoría, mostrar todos los productos
        productos = Producto.query.filter(Producto.cantidad > 0).all()

    productos_out_of_stock = Producto.query.filter_by(cantidad=0).all()

    return render_template('index.html', productos=productos, productos_out_of_stock=productos_out_of_stock, categoria=categoria, query=query)

@app.route('/surtir_producto', methods=['GET'])
@login_required
def surtir_producto():
    return render_template('surtir_producto.html')


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


# Rutas para manejar productos y demás...
@app.route('/editar_producto/<int:producto_id>', methods=['GET', 'POST'])
@login_required
def editar_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)  # Buscar el producto por ID

    if request.method == 'POST':  # Si es un POST (cuando el formulario se envía)
        producto.nombre = request.form['nombre']  # Obtener datos del formulario
        producto.cantidad = int(request.form['cantidad'])
        producto.categoria = request.form['categoria']

        # Verificar si se ha subido una nueva imagen
        if 'imagen' in request.files:
            imagen = request.files['imagen']
            if imagen and allowed_file(imagen.filename):
                filename = secure_filename(imagen.filename)
                imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                producto.imagen_url = filename  # Guardar la nueva imagen

        db.session.commit()  # Guardar cambios en la base de datos
        flash('Producto actualizado correctamente', 'success')
        return redirect(url_for('index'))  # Redirigir a la página principal

    # Si la petición es GET, se muestra el formulario de edición
    return render_template('editar_producto.html', producto=producto)


# La ruta que maneja la edición debe ir antes de la sección final
if __name__ == '__main__':
    app.run(debug=True)


# Ruta para obtener los detalles del producto
@app.route('/producto/<int:producto_id>', methods=['GET'])
@login_required
def get_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    return {
        'id': producto.id,
        'nombre': producto.nombre,
        'cantidad': producto.cantidad,
        'categoria': producto.categoria,
        'imagen_url': producto.imagen_url
    }

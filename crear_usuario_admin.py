from app import db, Usuario, bcrypt

# Crear las tablas si no existen
db.create_all()

# Crear el hash de la contraseña
password_hash = bcrypt.generate_password_hash("admin123").decode('utf-8')

# Crear el nuevo usuario
usuario_admin = Usuario(
    nombre="admin", 
    rol="superadmin",  # Asignamos el rol de 'superadmin'
    contrasena=password_hash
)

# Agregar y guardar el usuario en la base de datos
db.session.add(usuario_admin)
db.session.commit()

print("Usuario administrador creado con éxito")

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# La contraseña en texto plano
contrasena_plana = "123"

# Generar el hash
hashed_password = bcrypt.generate_password_hash(contrasena_plana).decode('utf-8')

print(hashed_password)  # Guarda este hash


# Para verificar la contraseña

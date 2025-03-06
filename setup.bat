@echo off
echo Instalando dependencias...
pip install flask
pip install flask-login
pip install flask-sqlalchemy
pip install flask-migrate
pip install flask-bcrypt
pip install werkzeug
pip install sqlalchemy
pip install alembic

echo.
echo Instalación completada!
echo Ejecuta la aplicación con: python app.py
pause
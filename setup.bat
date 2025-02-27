@echo off
echo Instalando dependencias...
pip install flask 
flask-login 
flask-sqlalchemy 
flask-migrate 
werkzeug

echo.
echo Instalación completada!
echo Ejecuta la aplicación con: python app.py
pause
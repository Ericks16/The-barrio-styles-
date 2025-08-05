from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "¡Aplicación funcionando correctamente!"

@app.route('/<path:path>')
def catch_all(path):
    return f"Ruta: {path}"

# Para Vercel, necesitas exportar la app
def handler(request):
    return app(request.environ, start_response)

# Para desarrollo local
if __name__ == '__main__':
    app.run(debug=True)

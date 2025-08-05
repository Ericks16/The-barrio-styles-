# =============================================================================
# app.py - Aplicación Flask optimizada para Vercel
# Enfoque en rendimiento, sostenibilidad y escalabilidad
# =============================================================================

from flask import Flask, request, jsonify, send_file, render_template_string
import os
import json
import logging
import time
from functools import wraps
from werkzeug.exceptions import NotFound

# Configuración de logging optimizada
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicialización de Flask con configuración de producción
app = Flask(__name__)

# Configuración optimizada para rendimiento
app.config.update(
    JSON_SORT_KEYS=False,
    JSONIFY_PRETTYPRINT_REGULAR=False,
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max upload
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
)

# Cache simple en memoria para mejorar rendimiento
_app_cache = {}
CACHE_TTL = 300  # 5 minutos

def cache_response(ttl=CACHE_TTL):
    """Decorator para cachear respuestas y optimizar rendimiento"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Generar clave de cache única
            cache_key = f"{f.__name__}_{request.method}_{request.path}_{str(args)}"
            current_time = time.time()
            
            # Verificar si existe en cache y no ha expirado
            if cache_key in _app_cache:
                cached_result, timestamp = _app_cache[cache_key]
                if current_time - timestamp < ttl:
                    logger.info(f"Cache hit para {cache_key}")
                    return cached_result
            
            # Ejecutar función y guardar en cache
            result = f(*args, **kwargs)
            _app_cache[cache_key] = (result, current_time)
            
            # Limpieza automática del cache para sostenibilidad
            if len(_app_cache) > 50:  # Límite de entradas
                oldest_key = min(_app_cache.keys(), 
                               key=lambda k: _app_cache[k][1])
                del _app_cache[oldest_key]
                logger.info("Cache cleanup ejecutado")
            
            return result
        return wrapper
    return decorator

def handle_errors(f):
    """Decorator para manejo robusto de errores"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except NotFound:
            return jsonify({
                'error': 'Recurso no encontrado',
                'message': 'La ruta solicitada no existe'
            }), 404
        except Exception as e:
            logger.error(f"Error en {f.__name__}: {str(e)}", exc_info=True)
            return jsonify({
                'error': 'Error interno del servidor',
                'message': 'Ocurrió un error inesperado'
            }), 500
    return wrapper

# =============================================================================
# RUTAS DE LA APLICACIÓN
# =============================================================================

@app.route('/')
@cache_response(ttl=600)  # Cache de 10 minutos para la página principal
@handle_errors
def home():
    """Página principal con diseño elegante y responsive"""
    html_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Aplicación Flask desplegada en Vercel">
        <title>🚀 App Flask - Vercel</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 1rem;
            }
            
            .container {
                background: rgba(255, 255, 255, 0.95);
                padding: 3rem;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                text-align: center;
                max-width: 600px;
                width: 100%;
                backdrop-filter: blur(10px);
            }
            
            .logo {
                font-size: 4rem;
                margin-bottom: 1rem;
                background: linear-gradient(135deg, #667eea, #764ba2);
                background-clip: text;
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            h1 {
                font-size: 2.5rem;
                margin-bottom: 1rem;
                color: #2d3748;
                font-weight: 700;
            }
            
            .status {
                display: inline-block;
                background: linear-gradient(135deg, #48bb78, #38a169);
                color: white;
                padding: 0.5rem 1.5rem;
                border-radius: 50px;
                font-weight: 600;
                margin-bottom: 2rem;
                box-shadow: 0 4px 15px rgba(72, 187, 120, 0.3);
            }
            
            .description {
                font-size: 1.1rem;
                color: #4a5568;
                margin-bottom: 2rem;
                line-height: 1.7;
            }
            
            .features {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 1rem;
                margin-bottom: 2rem;
            }
            
            .feature {
                background: #f7fafc;
                padding: 1rem;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }
            
            .feature-icon {
                font-size: 1.5rem;
                margin-bottom: 0.5rem;
            }
            
            .endpoints {
                background: #2d3748;
                color: white;
                padding: 1.5rem;
                border-radius: 10px;
                text-align: left;
                margin-top: 2rem;
            }
            
            .endpoints h3 {
                margin-bottom: 1rem;
                color: #667eea;
            }
            
            .endpoint {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0.5rem 0;
                border-bottom: 1px solid #4a5568;
            }
            
            .endpoint:last-child {
                border-bottom: none;
            }
            
            .method {
                background: #667eea;
                color: white;
                padding: 0.2rem 0.5rem;
                border-radius: 4px;
                font-size: 0.8rem;
                font-weight: 600;
            }
            
            .method.post {
                background: #48bb78;
            }
            
            @media (max-width: 768px) {
                .container {
                    margin: 1rem;
                    padding: 2rem;
                }
                
                h1 {
                    font-size: 2rem;
                }
                
                .features {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🚀</div>
            <h1>Flask App Desplegada</h1>
            <div class="status">✅ Funcionando Perfectamente</div>
            <p class="description">
                Aplicación Flask optimizada para producción con configuración 
                de alto rendimiento, sostenibilidad y escalabilidad en Vercel.
            </p>
            
            <div class="features">
                <div class="feature">
                    <div class="feature-icon">⚡</div>
                    <strong>Rendimiento</strong><br>
                    Cache optimizado y respuestas rápidas
                </div>
                <div class="feature">
                    <div class="feature-icon">🌱</div>
                    <strong>Sostenible</strong><br>
                    Gestión eficiente de recursos
                </div>
                <div class="feature">
                    <div class="feature-icon">📈</div>
                    <strong>Escalable</strong><br>
                    Arquitectura serverless preparada
                </div>
                <div class="feature">
                    <div class="feature-icon">🔒</div>
                    <strong>Seguro</strong><br>
                    Headers de seguridad configurados
                </div>
            </div>
            
            <div class="endpoints">
                <h3>📍 API Endpoints Disponibles</h3>
                <div class="endpoint">
                    <span><span class="method">GET</span> /</span>
                    <span>Página principal</span>
                </div>
                <div class="endpoint">
                    <span><span class="method">GET</span> /api/health</span>
                    <span>Estado de la aplicación</span>
                </div>
                <div class="endpoint">
                    <span><span class="method">GET</span> /api/test</span>
                    <span>Endpoint de prueba</span>
                </div>
                <div class="endpoint">
                    <span><span class="method post">POST</span> /api/data</span>
                    <span>Procesamiento de datos</span>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/api/health')
@cache_response(ttl=60)  # Cache de 1 minuto para health check
@handle_errors
def health_check():
    """Endpoint de salud para monitoreo y debugging"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'version': '1.0.0',
        'environment': os.environ.get('VERCEL_ENV', 'development'),
        'python_version': os.sys.version,
        'cache_entries': len(_app_cache),
        'uptime': 'Serverless - No persistent uptime'
    })

@app.route('/api/test')
@handle_errors
def test_endpoint():
    """Endpoint de prueba con información detallada del request"""
    return jsonify({
        'message': '✅ Test exitoso',
        'request_info': {
            'method': request.method,
            'path': request.path,
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'ip': request.headers.get('X-Forwarded-For', request.remote_addr),
            'content_type': request.content_type,
            'timestamp': time.time()
        },
        'server_info': {
            'vercel_env': os.environ.get('VERCEL_ENV', 'local'),
            'vercel_region': os.environ.get('VERCEL_REGION', 'unknown')
        }
    })

@app.route('/api/data', methods=['POST'])
@handle_errors
def process_data():
    """Endpoint para procesamiento de datos con validación robusta"""
    try:
        # Validar Content-Type
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type debe ser application/json'
            }), 400
        
        data = request.get_json()
        
        # Validar que se enviaron datos
        if not data:
            return jsonify({
                'error': 'No se proporcionaron datos en el body'
            }), 400
        
        # Procesamiento de datos con métricas
        start_time = time.time()
        
        processed_result = {
            'input_data': data,
            'metadata': {
                'processed_at': time.time(),
                'processing_time_ms': round((time.time() - start_time) * 1000, 2),
                'data_type': type(data).__name__,
                'data_size_bytes': len(json.dumps(data)),
                'keys_count': len(data) if isinstance(data, dict) else None
            },
            'processing_summary': {
                'status': 'success',
                'items_processed': len(data) if hasattr(data, '__len__') else 1,
                'validation_passed': True
            }
        }
        
        return jsonify({
            'success': True,
            'message': 'Datos procesados correctamente',
            'result': processed_result
        })
        
    except json.JSONDecodeError as e:
        return jsonify({
            'error': 'JSON inválido',
            'details': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error procesando datos: {str(e)}")
        return jsonify({
            'error': 'Error en el procesamiento',
            'message': 'Verifica el formato de los datos enviados'
        }), 500

# =============================================================================
# MANEJADORES DE ERRORES GLOBALES
# =============================================================================

@app.errorhandler(404)
def not_found_error(error):
    """Manejo elegante de rutas no encontradas"""
    return jsonify({
        'error': 'Endpoint no encontrado',
        'message': f'La ruta "{request.path}" no existe',
        'available_endpoints': {
            'GET': ['/', '/api/health', '/api/test'],
            'POST': ['/api/data']
        },
        'suggestion': 'Verifica la URL y el método HTTP'
    }), 404

@app.errorhandler(405)
def method_not_allowed_error(error):
    """Manejo de métodos HTTP no permitidos"""
    return jsonify({
        'error': 'Método no permitido',
        'message': f'El método {request.method} no está permitido para {request.path}',
        'allowed_methods': error.valid_methods
    }), 405

@app.errorhandler(500)
def internal_error(error):
    """Manejo de errores internos del servidor"""
    logger.error(f"Error 500: {str(error)}", exc_info=True)
    return jsonify({
        'error': 'Error interno del servidor',
        'message': 'Ocurrió un error inesperado. Intenta nuevamente.',
        'timestamp': time.time()
    }), 500

# =============================================================================
# CONFIGURACIÓN DE HEADERS DE SEGURIDAD Y RENDIMIENTO
# =============================================================================

@app.after_request
def after_request(response):
    """Configurar headers de seguridad y rendimiento para todas las respuestas"""
    
    # Headers de seguridad
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Headers de rendimiento
    if request.endpoint in ['home', 'health_check']:
        response.headers['Cache-Control'] = 'public, max-age=300'  # 5 minutos
    else:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    
    # CORS para APIs
    if request.path.startswith('/api/'):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    
    # Header personalizado para identificar la app
    response.headers['X-Powered-By'] = 'Flask-Vercel-Optimized'
    
    return response

# =============================================================================
# FUNCIÓN PRINCIPAL PARA VERCEL
# =============================================================================

def app_handler(environ, start_response):
    """
    Handler WSGI optimizado para Vercel
    Maneja la aplicación Flask en entorno serverless
    """
    try:
        return app(environ, start_response)
    except Exception as e:
        logger.error(f"Error en WSGI handler: {str(e)}", exc_info=True)
        # Respuesta de error en caso de fallo crítico
        start_response('500 Internal Server Error', [
            ('Content-Type', 'application/json'),
            ('Access-Control-Allow-Origin', '*')
        ])
        return [json.dumps({
            'error': 'Error crítico del servidor',
            'message': 'Contacta al administrador'
        }).encode('utf-8')]

# Para compatibilidad con Vercel, exportar app
handler = app_handler

# =============================================================================
# CONFIGURACIÓN PARA DESARROLLO LOCAL
# =============================================================================

if __name__ == '__main__':
    # Solo para desarrollo local
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🚀 Iniciando servidor Flask en puerto {port}")
    print(f"🔧 Modo debug: {'Activado' if debug_mode else 'Desactivado'}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode,
        threaded=True
    )
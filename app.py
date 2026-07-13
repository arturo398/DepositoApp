from flask import Flask, jsonify, request, render_template, send_file, session, redirect, url_for
import os
import tempfile

from backend.db import (
    init_db,
    get_productos,
    get_producto_by_id,
    crear_producto,
    registrar_movimiento,
    get_categorias,
    get_areas,
    get_transacciones,
    verificar_credenciales,
    eliminar_producto,
    actualizar_password
)
from backend.reports import generate_excel_report, generate_pdf_report

app = Flask(
    __name__,
    template_folder='templates',
    static_folder='static'
)

# Clave secreta para firmar las cookies de sesión
app.secret_key = os.environ.get('SECRET_KEY') or 'deposito-secreto-key-local-12345'

# Initialize database
init_db()

@app.before_request
def check_login():
    # Rutas públicas que no requieren inicio de sesión
    open_paths = [
        '/login',
        '/api/login',
        '/static'
    ]
    
    # Comprobar si la ruta solicitada empieza con alguna de las rutas públicas
    is_open = any(request.path.startswith(path) for path in open_paths)
    if is_open:
        return
        
    # Redirigir si no hay sesión activa
    if 'usuario' not in session:
        if request.path.startswith('/api/'):
            return jsonify({'error': 'No autorizado. Por favor inicia sesión.'}), 401
        return redirect(url_for('login_page'))

@app.route('/login', methods=['GET'])
def login_page():
    if 'usuario' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    usuario = data.get('usuario', '').strip()
    password = data.get('password', '')
    
    if not usuario or not password:
        return jsonify({'error': 'El usuario y la contraseña son obligatorios.'}), 400
        
    try:
        user_data = verificar_credenciales(usuario, password)
        if user_data:
            session['usuario'] = user_data['usuario']
            session['nombre'] = user_data['nombre']
            return jsonify({
                'success': True,
                'message': 'Inicio de sesión exitoso.',
                'usuario': user_data
            }), 200
        return jsonify({'error': 'Usuario o contraseña incorrectos.'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logout', methods=['POST', 'GET'])
def api_logout():
    session.pop('usuario', None)
    session.pop('nombre', None)
    if request.method == 'POST':
        return jsonify({'success': True, 'message': 'Sesión cerrada con éxito.'})
    return redirect(url_for('login_page'))

@app.route('/api/session-status', methods=['GET'])
def api_session_status():
    if 'usuario' in session:
        return jsonify({
            'autenticado': True,
            'usuario': session['usuario'],
            'nombre': session['nombre']
        }), 200
    return jsonify({'autenticado': False}), 401

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/productos', methods=['GET'])
def api_get_productos():
    query = request.args.get('q', '')
    categoria = request.args.get('categoria', '')
    try:
        productos = get_productos(query=query, categoria=categoria)
        return jsonify(productos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/productos/<int:producto_id>', methods=['GET'])
def api_get_producto(producto_id):
    try:
        producto = get_producto_by_id(producto_id)
        if producto:
            return jsonify(producto)
        return jsonify({'error': 'Producto no encontrado.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/productos', methods=['POST'])
def api_crear_producto():
    data = request.get_json() or {}
    nombre = data.get('nombre', '').strip()
    categoria = data.get('categoria', '').strip()
    cantidad_inicial = data.get('cantidad_inicial', 0)
    stock_minimo = data.get('stock_minimo', 0)
    
    if not nombre:
        return jsonify({'error': 'El nombre del producto es obligatorio.'}), 400
    if not categoria:
        return jsonify({'error': 'La categoría del producto es obligatoria.'}), 400
        
    try:
        cantidad_inicial = int(cantidad_inicial)
        stock_minimo = int(stock_minimo)
        if cantidad_inicial < 0 or stock_minimo < 0:
            raise ValueError()
    except ValueError:
        return jsonify({'error': 'Las cantidades deben ser números enteros no negativos.'}), 400
        
    try:
        producto_id = crear_producto(
            nombre=nombre,
            categoria=categoria,
            cantidad_inicial=cantidad_inicial,
            stock_minimo=stock_minimo
        )
        return jsonify({
            'success': True,
            'message': 'Producto creado con éxito.',
            'producto_id': producto_id
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transacciones', methods=['POST'])
def api_crear_transaccion():
    data = request.get_json() or {}
    producto_id = data.get('producto_id')
    tipo = data.get('tipo', '').strip().lower()
    cantidad = data.get('cantidad')
    area_destino = data.get('area_destino', '').strip()
    
    if not producto_id:
        return jsonify({'error': 'ID del producto es obligatorio.'}), 400
    if tipo not in ['entrada', 'salida']:
        return jsonify({'error': "El tipo de transacción debe ser 'entrada' o 'salida'."}), 400
    
    try:
        producto_id = int(producto_id)
        cantidad = int(cantidad)
        if cantidad <= 0:
            raise ValueError()
    except ValueError:
        return jsonify({'error': 'La cantidad debe ser un número entero mayor que cero.'}), 400
        
    if tipo == 'salida' and not area_destino:
        return jsonify({'error': 'El área de trabajo de destino es obligatoria para salidas.'}), 400
        
    try:
        registrar_movimiento(
            producto_id=producto_id,
            tipo=tipo,
            cantidad=cantidad,
            area_destino=area_destino if tipo == 'salida' else None
        )
        return jsonify({
            'success': True,
            'message': f"Movimiento de {tipo} registrado con éxito."
        }), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/categorias', methods=['GET'])
def api_get_categorias():
    try:
        categorias = get_categorias()
        return jsonify(categorias)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/areas', methods=['GET'])
def api_get_areas():
    try:
        areas = get_areas()
        return jsonify(areas)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transacciones', methods=['GET'])
def api_get_transacciones():
    limit = request.args.get('limit', 200)
    try:
        limit = int(limit)
    except ValueError:
        limit = 200
        
    try:
        transacciones = get_transacciones(limit=limit)
        return jsonify(transacciones)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reportes/excel', methods=['GET'])
def download_excel_report():
    try:
        # Create temp file
        temp_dir = tempfile.gettempdir()
        filename = f"reporte_deposito_{os.urandom(4).hex()}.xlsx"
        filepath = os.path.join(temp_dir, filename)
        
        generate_excel_report(filepath)
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=f"Reporte_Deposito_{os.urandom(4).hex()}.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reportes/pdf', methods=['GET'])
def download_pdf_report():
    try:
        # Create temp file
        temp_dir = tempfile.gettempdir()
        filename = f"reporte_deposito_{os.urandom(4).hex()}.pdf"
        filepath = os.path.join(temp_dir, filename)
        
        generate_pdf_report(filepath)
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=f"Reporte_Deposito_{os.urandom(4).hex()}.pdf",
            mimetype="application/pdf"
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/productos/<int:producto_id>', methods=['DELETE'])
def api_eliminar_producto(producto_id):
    try:
        # Check if product exists first
        p = get_producto_by_id(producto_id)
        if not p:
            return jsonify({'error': 'El producto no existe.'}), 404
            
        eliminar_producto(producto_id)
        return jsonify({
            'success': True,
            'message': f"Producto '{p['nombre']}' eliminado del inventario con éxito."
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cambiar-password', methods=['POST'])
def api_cambiar_password():
    data = request.get_json() or {}
    password_actual = data.get('password_actual', '')
    password_nuevo = data.get('password_nuevo', '')
    
    if not password_actual or not password_nuevo:
        return jsonify({'error': 'La contraseña actual y la nueva son obligatorias.'}), 400
        
    usuario = session.get('usuario')
    if not usuario:
        return jsonify({'error': 'No autorizado.'}), 401
        
    try:
        # Verify current password
        user_check = verificar_credenciales(usuario, password_actual)
        if not user_check:
            return jsonify({'error': 'La contraseña actual es incorrecta.'}), 400
            
        actualizar_password(usuario, password_nuevo)
        return jsonify({
            'success': True,
            'message': 'Contraseña modificada con éxito.'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # '0.0.0.0' permite conexiones desde cualquier dispositivo de la red local (LAN)
    app.run(host='0.0.0.0', debug=True, port=5000)


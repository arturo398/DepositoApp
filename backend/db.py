import sqlite3
import os
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

try:
    import pg8000.dbapi
except ImportError:
    pg8000 = None

# Helper to load .env file manually
def load_dotenv():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
    env_path = os.path.join(base_dir, '.env')
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, val = line.split('=', 1)
                        os.environ[key.strip()] = val.strip()
        except Exception as e:
            print(f"Error loading .env file: {e}", file=sys.stderr)

# Run .env loading
load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')
IS_POSTGRES = DATABASE_URL is not None
DB_PARAM = '%s' if IS_POSTGRES else '?'

# Local SQLite fallback path
if os.environ.get('VERCEL'):
    DATABASE_PATH = os.environ.get('DB_PATH') or '/tmp/database.db'
elif getattr(sys, 'frozen', False):
    DATABASE_PATH = os.environ.get('DB_PATH') or os.path.join(os.path.dirname(sys.executable), 'database.db')
else:
    DATABASE_PATH = os.environ.get('DB_PATH') or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database.db')

def get_db_connection():
    if IS_POSTGRES:
        if pg8000 is None:
            raise ImportError("La librería 'pg8000' no está instalada en el entorno pero es necesaria para PostgreSQL.")
        from urllib.parse import urlparse
        import ssl
        # Parse connection string
        result = urlparse(DATABASE_URL)
        
        # Create standard SSL context (Supabase/Neon and other cloud providers require SSL)
        ssl_ctx = ssl.create_default_context()
        # Disable certificate verification to prevent CERTIFICATE_VERIFY_FAILED on Windows
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        
        conn = pg8000.dbapi.connect(
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port or 5432,
            database=result.path[1:],
            ssl_context=ssl_ctx
        )
        return conn
    else:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

def make_dict_cursor(cursor):
    class DictCursorWrapper:
        def __init__(self, cur):
            self._cur = cur
        def __getattr__(self, name):
            return getattr(self._cur, name)
        def fetchone(self):
            row = self._cur.fetchone()
            if row is None:
                return None
            columns = [col[0] for col in self._cur.description]
            return dict(zip(columns, row))
        def fetchall(self):
            rows = self._cur.fetchall()
            if not rows:
                return []
            columns = [col[0] for col in self._cur.description]
            return [dict(zip(columns, r)) for r in rows]
    return DictCursorWrapper(cursor)

def get_cursor(conn):
    cursor = conn.cursor()
    if IS_POSTGRES:
        return make_dict_cursor(cursor)
    return cursor

def init_db():
    conn = get_db_connection()
    cursor = get_cursor(conn)
    try:
        if IS_POSTGRES:
            # PostgreSQL Table Initialization
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS productos (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    categoria VARCHAR(255) NOT NULL,
                    cantidad INTEGER NOT NULL DEFAULT 0,
                    stock_minimo INTEGER NOT NULL DEFAULT 0
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transacciones (
                    id SERIAL PRIMARY KEY,
                    producto_id INTEGER NOT NULL,
                    tipo VARCHAR(50) NOT NULL CHECK(tipo IN ('entrada', 'salida')),
                    cantidad INTEGER NOT NULL,
                    area_destino VARCHAR(255),
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    usuario VARCHAR(255) NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    nombre VARCHAR(255)
                )
            ''')
            
            # Seed default user if none exists
            cursor.execute("SELECT COUNT(*) as count FROM usuarios")
            if cursor.fetchone()['count'] == 0:
                default_hash = generate_password_hash("admin123")
                cursor.execute(
                    "INSERT INTO usuarios (usuario, password_hash, nombre) VALUES ('admin', %s, 'Administrador')",
                    (default_hash,)
                )
        else:
            # SQLite Table Initialization
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    categoria TEXT NOT NULL,
                    cantidad INTEGER NOT NULL DEFAULT 0,
                    stock_minimo INTEGER NOT NULL DEFAULT 0
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transacciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    producto_id INTEGER NOT NULL,
                    tipo TEXT NOT NULL CHECK(tipo IN ('entrada', 'salida')),
                    cantidad INTEGER NOT NULL,
                    area_destino TEXT,
                    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    nombre TEXT
                )
            ''')
            
            # Seed default user if none exists
            cursor.execute("SELECT COUNT(*) as count FROM usuarios")
            if cursor.fetchone()['count'] == 0:
                default_hash = generate_password_hash("admin123")
                cursor.execute(
                    "INSERT INTO usuarios (usuario, password_hash, nombre) VALUES ('admin', ?, 'Administrador')",
                    (default_hash,)
                )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_productos(query=None, categoria=None):
    conn = get_db_connection()
    cursor = get_cursor(conn)
    
    sql = "SELECT id, nombre, categoria, cantidad, stock_minimo FROM productos WHERE 1=1"
    params = []
    
    if query:
        if query.isdigit():
            sql += f" AND (id = {DB_PARAM} OR nombre LIKE {DB_PARAM})"
            params.extend([int(query), f"%{query}%"])
        else:
            sql += f" AND nombre LIKE {DB_PARAM}"
            params.append(f"%{query}%")
            
    if categoria:
        sql += f" AND categoria = {DB_PARAM}"
        params.append(categoria)
        
    sql += " ORDER BY id ASC"
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    productos = [dict(row) for row in rows]
    conn.close()
    return productos

def get_producto_by_id(producto_id):
    conn = get_db_connection()
    cursor = get_cursor(conn)
    cursor.execute(f"SELECT id, nombre, categoria, cantidad, stock_minimo FROM productos WHERE id = {DB_PARAM}", (producto_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def crear_producto(nombre, categoria, cantidad_inicial=0, stock_minimo=0):
    conn = get_db_connection()
    cursor = get_cursor(conn)
    try:
        # Check if product with this name already exists
        cursor.execute(f"SELECT id, cantidad FROM productos WHERE LOWER(nombre) = LOWER({DB_PARAM})", (nombre.strip(),))
        existing = cursor.fetchone()
        
        if existing:
            producto_id = existing['id']
            nueva_cantidad = existing['cantidad'] + cantidad_inicial
            
            # Update existing product quantity
            cursor.execute(
                f"UPDATE productos SET cantidad = {DB_PARAM} WHERE id = {DB_PARAM}",
                (nueva_cantidad, producto_id)
            )
            
            # Record entry transaction if quantity > 0
            if cantidad_inicial > 0:
                cursor.execute(
                    f"INSERT INTO transacciones (producto_id, tipo, cantidad, area_destino) VALUES ({DB_PARAM}, 'entrada', {DB_PARAM}, NULL)",
                    (producto_id, cantidad_inicial)
                )
                
            conn.commit()
            return producto_id, False
            
        # Insert product
        if IS_POSTGRES:
            cursor.execute(
                "INSERT INTO productos (nombre, categoria, cantidad, stock_minimo) VALUES (%s, %s, %s, %s) RETURNING id",
                (nombre.strip(), categoria, cantidad_inicial, stock_minimo)
            )
            producto_id = cursor.fetchone()['id']
        else:
            cursor.execute(
                "INSERT INTO productos (nombre, categoria, cantidad, stock_minimo) VALUES (?, ?, ?, ?)",
                (nombre.strip(), categoria, cantidad_inicial, stock_minimo)
            )
            producto_id = cursor.lastrowid
        
        # If there's initial stock, record an initial entry transaction
        if cantidad_inicial > 0:
            cursor.execute(
                f"INSERT INTO transacciones (producto_id, tipo, cantidad, area_destino) VALUES ({DB_PARAM}, 'entrada', {DB_PARAM}, NULL)",
                (producto_id, cantidad_inicial)
            )
            
        conn.commit()
        return producto_id, True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def registrar_movimiento(producto_id, tipo, cantidad, area_destino=None):
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor que cero.")
        
    conn = get_db_connection()
    cursor = get_cursor(conn)
    try:
        # Check current stock
        cursor.execute(f"SELECT cantidad, nombre FROM productos WHERE id = {DB_PARAM}", (producto_id,))
        prod = cursor.fetchone()
        if not prod:
            raise ValueError("El producto no existe.")
            
        stock_actual = prod['cantidad']
        nombre_producto = prod['nombre']
        
        if tipo == 'salida' and stock_actual < cantidad:
            raise ValueError(f"Stock insuficiente para {nombre_producto}. Stock actual: {stock_actual}, solicitado: {cantidad}.")
            
        # Calculate new stock
        if tipo == 'entrada':
            nuevo_stock = stock_actual + cantidad
        else:
            nuevo_stock = stock_actual - cantidad
            
        # Record transaction
        cursor.execute(
            f"INSERT INTO transacciones (producto_id, tipo, cantidad, area_destino) VALUES ({DB_PARAM}, {DB_PARAM}, {DB_PARAM}, {DB_PARAM})",
            (producto_id, tipo, cantidad, area_destino.strip() if area_destino else None)
        )
        
        # Update product stock
        cursor.execute(
            f"UPDATE productos SET cantidad = {DB_PARAM} WHERE id = {DB_PARAM}",
            (nuevo_stock, producto_id)
        )
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_categorias():
    conn = get_db_connection()
    cursor = get_cursor(conn)
    cursor.execute("SELECT DISTINCT categoria FROM productos WHERE categoria != '' ORDER BY categoria ASC")
    rows = cursor.fetchall()
    categorias = [row['categoria'] for row in rows]
    conn.close()
    return categorias

def get_areas():
    conn = get_db_connection()
    cursor = get_cursor(conn)
    cursor.execute("SELECT DISTINCT area_destino FROM transacciones WHERE area_destino IS NOT NULL AND area_destino != '' ORDER BY area_destino ASC")
    rows = cursor.fetchall()
    areas = [row['area_destino'] for row in rows]
    conn.close()
    return areas

def get_transacciones(limit=200, producto_id=None, area=None, fecha_inicio=None, fecha_fin=None, tipo=None):
    conn = get_db_connection()
    cursor = get_cursor(conn)
    
    query = '''
        SELECT t.id, t.producto_id, p.nombre AS producto_nombre, p.categoria AS producto_categoria, 
               t.tipo, t.cantidad, t.area_destino, t.fecha 
        FROM transacciones t
        JOIN productos p ON t.producto_id = p.id
        WHERE 1=1
    '''
    params = []
    
    if producto_id:
        query += f" AND t.producto_id = {DB_PARAM}"
        params.append(producto_id)
        
    if area:
        query += f" AND t.area_destino = {DB_PARAM}"
        params.append(area)

    if tipo:
        query += f" AND t.tipo = {DB_PARAM}"
        params.append(tipo)
        
    if fecha_inicio:
        if IS_POSTGRES:
            query += f" AND t.fecha::date >= {DB_PARAM}::date"
        else:
            query += f" AND DATE(t.fecha) >= DATE({DB_PARAM})"
        params.append(fecha_inicio)
        
    if fecha_fin:
        if IS_POSTGRES:
            query += f" AND t.fecha::date <= {DB_PARAM}::date"
        else:
            query += f" AND DATE(t.fecha) <= DATE({DB_PARAM})"
        params.append(fecha_fin)
        
    query += f" ORDER BY t.fecha DESC, t.id DESC LIMIT {DB_PARAM}"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    # Process rows to ensure JSON serializability and string dates
    transacciones = []
    for row in rows:
        d = dict(row)
        if isinstance(d['fecha'], datetime):
            d['fecha'] = d['fecha'].strftime("%Y-%m-%d %H:%M:%S")
        transacciones.append(d)
        
    conn.close()
    return transacciones

def crear_usuario(usuario, password, nombre):
    conn = get_db_connection()
    cursor = get_cursor(conn)
    try:
        password_hash = generate_password_hash(password)
        cursor.execute(
            f"INSERT INTO usuarios (usuario, password_hash, nombre) VALUES ({DB_PARAM}, {DB_PARAM}, {DB_PARAM})",
            (usuario.strip().lower(), password_hash, nombre.strip())
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def verificar_credenciales(usuario, password):
    conn = get_db_connection()
    cursor = get_cursor(conn)
    cursor.execute(f"SELECT password_hash, nombre FROM usuarios WHERE usuario = {DB_PARAM}", (usuario.strip().lower(),))
    row = cursor.fetchone()
    conn.close()
    
    if row and check_password_hash(row['password_hash'], password):
        return {"usuario": usuario.strip().lower(), "nombre": row['nombre']}
    return None

def eliminar_producto(producto_id):
    conn = get_db_connection()
    cursor = get_cursor(conn)
    try:
        cursor.execute(f"DELETE FROM productos WHERE id = {DB_PARAM}", (producto_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def actualizar_password(usuario, nuevo_password):
    conn = get_db_connection()
    cursor = get_cursor(conn)
    try:
        password_hash = generate_password_hash(nuevo_password)
        cursor.execute(
            f"UPDATE usuarios SET password_hash = {DB_PARAM} WHERE usuario = {DB_PARAM}",
            (password_hash, usuario.strip().lower())
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

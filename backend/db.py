import sqlite3
import os

# Permite configurar una ruta externa persistente para la base de datos en servidores de produccion
if os.environ.get('VERCEL'):
    DATABASE_PATH = os.environ.get('DB_PATH') or '/tmp/database.db'
else:
    DATABASE_PATH = os.environ.get('DB_PATH') or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            cantidad INTEGER NOT NULL DEFAULT 0,
            stock_minimo INTEGER NOT NULL DEFAULT 0
        )
    ''')
    
    # Create transactions table
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

    # Create users table
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
        # pyrefly: ignore [missing-import]
        from werkzeug.security import generate_password_hash
        default_hash = generate_password_hash("admin123")
        cursor.execute(
            "INSERT INTO usuarios (usuario, password_hash, nombre) VALUES ('admin', ?, 'Administrador')",
            (default_hash,)
        )
    
    conn.commit()
    conn.close()

def get_productos(query=None, categoria=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = "SELECT id, nombre, categoria, cantidad, stock_minimo FROM productos WHERE 1=1"
    params = []
    
    if query:
        # Search by id (if integer-like) or name (LIKE)
        if query.isdigit():
            sql += " AND (id = ? OR nombre LIKE ?)"
            params.extend([int(query), f"%{query}%"])
        else:
            sql += " AND nombre LIKE ?"
            params.append(f"%{query}%")
            
    if categoria:
        sql += " AND categoria = ?"
        params.append(categoria)
        
    sql += " ORDER BY id ASC"
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    productos = [dict(row) for row in rows]
    conn.close()
    return productos

def get_producto_by_id(producto_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, categoria, cantidad, stock_minimo FROM productos WHERE id = ?", (producto_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def crear_producto(nombre, categoria, cantidad_inicial=0, stock_minimo=0):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Insert product
        cursor.execute(
            "INSERT INTO productos (nombre, categoria, cantidad, stock_minimo) VALUES (?, ?, ?, ?)",
            (nombre, categoria, cantidad_inicial, stock_minimo)
        )
        producto_id = cursor.lastrowid
        
        # If there's initial stock, record an initial entry transaction
        if cantidad_inicial > 0:
            cursor.execute(
                "INSERT INTO transacciones (producto_id, tipo, cantidad, area_destino) VALUES (?, 'entrada', ?, NULL)",
                (producto_id, cantidad_inicial)
            )
            
        conn.commit()
        return producto_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def registrar_movimiento(producto_id, tipo, cantidad, area_destino=None):
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor que cero.")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check current stock
        cursor.execute("SELECT cantidad, nombre FROM productos WHERE id = ?", (producto_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"El producto con ID {producto_id} no existe.")
            
        stock_actual = row['cantidad']
        nombre_producto = row['nombre']
        
        if tipo == 'salida':
            if stock_actual < cantidad:
                raise ValueError(f"Stock insuficiente para {nombre_producto}. Stock actual: {stock_actual}, solicitado: {cantidad}.")
            if not area_destino or not area_destino.strip():
                raise ValueError("Debe especificar un área de destino para las salidas de material.")
            nuevo_stock = stock_actual - cantidad
        elif tipo == 'entrada':
            nuevo_stock = stock_actual + cantidad
            area_destino = None # Entries do not have target areas
        else:
            raise ValueError("Tipo de movimiento inválido.")
            
        # Insert transaction
        cursor.execute(
            "INSERT INTO transacciones (producto_id, tipo, cantidad, area_destino) VALUES (?, ?, ?, ?)",
            (producto_id, tipo, cantidad, area_destino.strip() if area_destino else None)
        )
        
        # Update product stock
        cursor.execute(
            "UPDATE productos SET cantidad = ? WHERE id = ?",
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
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT categoria FROM productos WHERE categoria != '' ORDER BY categoria ASC")
    rows = cursor.fetchall()
    categorias = [row['categoria'] for row in rows]
    conn.close()
    return categorias

def get_areas():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT area_destino FROM transacciones WHERE area_destino IS NOT NULL AND area_destino != '' ORDER BY area_destino ASC")
    rows = cursor.fetchall()
    areas = [row['area_destino'] for row in rows]
    conn.close()
    return areas

def get_transacciones(limit=200):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.id, t.producto_id, p.nombre AS producto_nombre, p.categoria AS producto_categoria, 
               t.tipo, t.cantidad, t.area_destino, t.fecha 
        FROM transacciones t
        JOIN productos p ON t.producto_id = p.id
        ORDER BY t.fecha DESC, t.id DESC
        LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    transacciones = [dict(row) for row in rows]
    conn.close()
    return transacciones

def crear_usuario(usuario, password, nombre):
    # pyrefly: ignore [missing-import]
    from werkzeug.security import generate_password_hash
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        password_hash = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO usuarios (usuario, password_hash, nombre) VALUES (?, ?, ?)",
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
    # pyrefly: ignore [missing-import]
    from werkzeug.security import check_password_hash
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, nombre FROM usuarios WHERE usuario = ?", (usuario.strip().lower(),))
    row = cursor.fetchone()
    conn.close()
    
    if row and check_password_hash(row['password_hash'], password):
        return {"usuario": usuario.strip().lower(), "nombre": row['nombre']}
    return None

def eliminar_producto(producto_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def actualizar_password(usuario, nuevo_password):
    from werkzeug.security import generate_password_hash
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        password_hash = generate_password_hash(nuevo_password)
        cursor.execute(
            "UPDATE usuarios SET password_hash = ? WHERE usuario = ?",
            (password_hash, usuario.strip().lower())
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


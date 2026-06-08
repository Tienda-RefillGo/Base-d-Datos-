import sqlite3
import os

class RefillManager:
    """Clase que administra la persistencia y operaciones de Base de Datos de Refill Go"""
    
    def __init__(self, db_name="tienda_v2.sqlite3"):
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.db_path = os.path.join(self.basedir, db_name)
        self.inicializar_tablas()

    def get_conexion(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def inicializar_tablas(self):
        conn = self.get_conexion()
        
        # 1. Tabla de Usuarios
        conn.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL, pedidos INTEGER DEFAULT 0,
                        imagen TEXT DEFAULT 'default_user.png')''')
        
        # 2. Tabla de Productos (Catálogo e Inventario)
        conn.execute('''CREATE TABLE IF NOT EXISTS productos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL, descripcion TEXT NOT NULL,
                        precio REAL NOT NULL, stock INTEGER NOT NULL, 
                        imagen TEXT, categoria TEXT NOT NULL)''')
        
        # 3. Tabla de Pedidos / Compras
        conn.execute('''CREATE TABLE IF NOT EXISTS pedidos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario_id INTEGER NOT NULL, productos_comprados TEXT NOT NULL,
                        direccion TEXT NOT NULL, codigo_postal TEXT NOT NULL,
                        metodo_pago TEXT NOT NULL, total REAL NOT NULL, fecha TEXT NOT NULL,
                        FOREIGN KEY (usuario_id) REFERENCES usuarios(id))''')
        
        # INYECCIÓN CORREGIDA: Sincronizada letra por letra con tu captura de VS Code
        cursor = conn.execute('SELECT COUNT(*) FROM productos')
        if cursor.fetchone()[0] == 0:
            productos_refill = [
                ('Cloro Concentrado 1L', 'Ideal para desinfección total de superficies y áreas comunes.', 25.00, 120, 'cloro.jpg.png', 'limpieza'),
                ('Detergente Multiusos 1L', 'Fórmula biodegradable de alto rendimiento para todo tipo de pisos.', 45.00, 100, 'detergente.png', 'limpieza'),
                ('Jabón Líquido Ropa 3L', 'Excelente remoción de manchas cuidando las fibras textiles.', 110.00, 40, 'jabon_liquidojpg.png', 'ropa'),
                ('Lavatrastes Cítrico 1L', 'Poder arrancagrasa inmediato con extractos naturales de plantas.', 38.00, 85, 'lavatrastes.jpg.png', 'cocina'),
                ('Limpiador de Pisos 2L', 'Brillo intenso y aroma premium persistente para el hogar.', 65.00, 50, 'limpiador.jpg.png', 'limpieza'),
                ('Shampoo Antiséptico 1L', 'Limpieza profunda de manos con PH balanceado y humectantes.', 42.00, 70, 'shampoo.jpg.png', 'limpieza'),
                ('Suavizante Libre de Plásticos 2L', 'Máxima suavidad y aroma prolongado libre de microplásticos.', 70.00, 60, 'suavizante.jpg.png', 'ropa')
            ]
            conn.executemany('INSERT INTO productos (nombre, descripcion, precio, stock, imagen, categoria) VALUES (?, ?, ?, ?, ?, ?)', productos_refill)
        
        conn.commit()
        conn.close()

    # --- MÉTODOS DE CONSULTA ---
    def obtener_todos_productos(self):
        conn = self.get_conexion()
        productos = conn.execute('SELECT * FROM productos').fetchall()
        conn.close()
        return productos

    def insertar_nuevo_producto(self, nombre, descripcion, precio, stock, imagen, categoria):
        conn = self.get_conexion()
        conn.execute('''INSERT INTO productos (nombre, descripcion, precio, stock, imagen, categoria) 
                        VALUES (?, ?, ?, ?, ?, ?)''', (nombre, descripcion, precio, stock, imagen, categoria))
        conn.commit()
        conn.close()

    def obtener_productos_por_lista_ids(self, lista_ids):
        if not lista_ids: return []
        conn = self.get_conexion()
        para_buscar = ','.join('?' for _ in lista_ids)
        productos = conn.execute(f'SELECT * FROM productos WHERE id IN ({para_buscar})', lista_ids).fetchall()
        conn.close()
        return productos

    def registrar_usuario(self, nombre, email, password):
        conn = self.get_conexion()
        conn.execute('INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)', (nombre, email, password))
        conn.commit()
        conn.close()

    def obtener_usuario_por_email(self, email):
        conn = self.get_conexion()
        user = conn.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()
        conn.close()
        return user

    def obtener_usuario_por_id(self, usuario_id):
        conn = self.get_conexion()
        user = conn.execute('SELECT * FROM usuarios WHERE id = ?', (usuario_id,)).fetchone()
        conn.close()
        return user

    def registrar_pedido(self, usuario_id, lista_productos_nombres, direccion, cp, metodo_pago, total):
        conn = self.get_conexion()
        productos_str = ", ".join(lista_productos_nombres)
        conn.execute('''INSERT INTO pedidos (usuario_id, productos_comprados, direccion, codigo_postal, metodo_pago, total, fecha) 
                        VALUES (?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))''', 
                     (usuario_id, productos_str, direccion, cp, metodo_pago, total))
        conn.execute('UPDATE usuarios SET pedidos = pedidos + 1 WHERE id = ?', (usuario_id,))
        conn.commit()
        conn.close()
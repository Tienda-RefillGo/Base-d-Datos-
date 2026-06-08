import os
import sqlite3

class RefillManager:
    def __init__(self, db_name="tienda_v2.sqlite3"):
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.db_path = os.path.join(self.basedir, db_name)
        self.inicializar_tablas()
        self.verificar_migraciones()
        self.insertar_datos_demo()

    def get_conexion(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def inicializar_tablas(self):
        conn = self.get_conexion()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                correo TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                tipo TEXT NOT NULL DEFAULT 'B2C',
                foto TEXT DEFAULT 'default_avatar.png'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                precio REAL NOT NULL,
                stock INTEGER NOT NULL,
                imagen TEXT DEFAULT 'default.png',
                categoria TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                total REAL NOT NULL,
                fecha TEXT NOT NULL,
                detalles TEXT NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        ''')
        conn.commit()
        conn.close()

    def verificar_migraciones(self):
        conn = self.get_conexion()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(usuarios);")
        columnas = [info[1] for info in cursor.fetchall()]
        if "foto" not in columnas:
            try:
                cursor.execute("ALTER TABLE usuarios ADD COLUMN foto TEXT DEFAULT 'default_avatar.png'")
                conn.commit()
            except sqlite3.OperationalError:
                pass
        conn.close()

    def insertar_datos_demo(self):
        """Asigna los nombres exactos de tus archivos en la carpeta static/img/."""
        conn = self.get_conexion()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM productos')
        if cursor.fetchone()[0] == 0:
            productos_demo = [
                ("Detergente Líquido Bio", "Fórmula concentrada biodegradable para ropa de color.", 38.50, 150, "detergente.png", "Ropa"),
                ("Lavatrastes Enzima Verde", "Elimina grasa severa sin dañar tus manos ni el agua.", 32.00, 200, "lavatrastes.jpg.png", "Limpieza"),
                ("Multiusos Pino Ecológico", "Desinfectante natural para pisos y superficies del hogar.", 28.00, 100, "limpiador.jpg.png", "Limpieza")
            ]
            cursor.executemany('''
                INSERT INTO productos (nombre, descripcion, precio, stock, imagen, categoria)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', productos_demo)
            
            cursor.execute('''
                INSERT OR IGNORE INTO usuarios (id, nombre, correo, password, tipo, foto)
                VALUES (1, 'Cliente Demo LCE', 'cliente@refillgo.com', '12345', 'B2C', 'default_avatar.png')
            ''')
            conn.commit()
        conn.close()

    def obtener_todos_productos(self):
        conn = self.get_conexion()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM productos')
        res = cursor.fetchall()
        conn.close()
        return res

    def obtener_usuario_por_id(self, usuario_id):
        conn = self.get_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
        res = cursor.fetchone()
        conn.close()
        return res
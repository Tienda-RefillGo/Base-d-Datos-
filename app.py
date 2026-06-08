import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from db_manager import RefillManager

app = Flask(__name__)
app.secret_key = "refillgo_lce_secret_key_2026"

# Inicializar nuestro gestor de base de datos relacional
db = RefillManager()

@app.route('/')
def index():
    """Página principal que expone el catálogo dinámico de productos."""
    return render_template('index.html')

@app.route('/api/productos')
def api_productos():
    """Endpoint API que retorna el catálogo en formato JSON para el frontend."""
    productos_db = db.obtener_todos_productos()
    lista_productos = []
    for p in productos_db:
        lista_productos.append({
            "id": p["id"],
            "nombre": p["nombre"],
            "descripcion": p["descripcion"],
            "precio": p["precio"],
            "stock": p["stock"],
            "imagen": p["imagen"],
            "categoria": p["categoria"]
        })
    return {"productos": lista_productos}

@app.route('/agregar_al_carrito', methods=['POST'])
def agregar_al_carrito():
    """Captura los datos del formulario e inyecta el producto en la sesión."""
    producto_id = request.form.get('producto_id')
    nombre = request.form.get('nombre')
    precio = float(request.form.get('precio', 0.0))
    imagen = request.form.get('imagen', 'default.png')
    
    if 'carrito' not in session:
        session['carrito'] = []
        
    carrito = session['carrito']
    
    # Comprobar si ya existe el producto para incrementar los litros
    encontrado = False
    for item in carrito:
        if str(item['id']) == str(producto_id):
            item['cantidad'] += 1
            encontrado = True
            break
            
    if not encontrado:
        carrito.append({
            'id': producto_id,
            'nombre': nombre,
            'precio': precio,
            'imagen': imagen,
            'cantidad': 1
        })
        
    session['carrito'] = carrito
    session.modified = True
    flash(f'¡{nombre} añadido al carrito circular!', 'success')
    return redirect(url_for('index'))

@app.route('/carrito')
def mostrar_carrito():
    """Despliega la vista transaccional calculando los subtotales de la orden."""
    carrito = session.get('carrito', [])
    total = sum(item['precio'] * item['cantidad'] for item in carrito)
    return render_template('carrito.html', carrito=carrito, total=total)

@app.route('/vaciar_carrito')
def vaciar_carrito():
    """Limpia la estructura temporal de la sesión del usuario."""
    session.pop('carrito', None)
    return redirect(url_for('mostrar_carrito'))

@app.route('/impacto-ecologico')
def impacto():
    """Muestra la sección informativa de sustentabilidad."""
    return render_template('impacto.html')

@app.route('/puntos-de-relleno')
def puntos():
    """Muestra la ubicación de las estaciones dispensadoras."""
    return render_template('puntos.html')

@app.route('/login')
def login():
    """Previene el quiebre de Jinja2 en base.html al proveer el endpoint."""
    return "<h3>Pantalla de Login de Refill Go — En Desarrollo Próximamente</h3><a href='/'>Volver al Catálogo</a>"
@app.route('/planes')
def planes():
    """Ruta de escape para evitar que Jinja2 rompa la compilación."""
    return redirect(url_for('puntos'))
if __name__ == '__main__':
    app.run(debug=True, port=5001)
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
from functools import wraps

# Configuración para subida de archivos
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Cargar variables de entorno
load_dotenv()

# Configuración de la aplicación Flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'clave-secreta-temporal')

# URL de la API
API_URL = os.getenv('API_URL', 'http://api:8000')

# Filtros personalizados para Jinja
@app.template_filter('fecha_bonita')
def fecha_bonita_filter(fecha_str):
    """Convierte una fecha ISO a un formato más amigable: DD/MM/YYYY HH:MM (hora Ecuador GMT-5)"""
    if not fecha_str:
        return ""
    try:
        from datetime import datetime, timedelta
        fecha_obj = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
        # Ajustar a hora de Ecuador (GMT-5)
        fecha_ecuador = fecha_obj - timedelta(hours=5)
        return fecha_ecuador.strftime('%d/%m/%Y %H:%M')
    except Exception as e:
        print(f"Error al formatear fecha con filtro: {str(e)}")
        return fecha_str

# Decorador para proteger rutas de administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'access_token' not in session or session.get('user_type') != 'admin':
            flash("Acceso restringido. Debe iniciar sesión como administrador.", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Rutas de la aplicación
@app.route('/')
def index():
    try:
        # Obtenemos los productos disponibles
        response = requests.get(f"{API_URL}/productos/")
        if response.status_code == 200:
            productos = response.json()
            return render_template('index.html', productos=productos[:3])  # Solo mostramos 3 productos en la página principal
        else:
            flash(f"Error al cargar productos: {response.status_code}", "danger")
            return render_template('index.html', productos=[])
    except Exception as e:
        flash(f"Error de conexión: {str(e)}", "danger")
        return render_template('index.html', productos=[])

@app.route('/productos')
def productos():
    try:
        # Obtenemos todos los productos
        response = requests.get(f"{API_URL}/productos/")
        if response.status_code == 200:
            productos = response.json()
            if not productos:
                flash("No hay productos disponibles en este momento. Vuelve a revisar más tarde.", "info")
            print(f"Productos cargados: {len(productos)}")
            # Depurar primeros 3 productos
            for i, producto in enumerate(productos[:3]):
                print(f"Producto {i+1}: ID={producto.get('id')}, Nombre={producto.get('nombre')}, Activo={producto.get('activo')}")
            return render_template('productos.html', productos=productos)
        else:
            error_msg = ""
            try:
                error_msg = response.json().get('detail', 'Error desconocido')
            except:
                error_msg = f"Código de error: {response.status_code}"
            flash(f"Error al cargar productos: {error_msg}", "danger")
            return render_template('productos.html', productos=[])
    except Exception as e:
        flash(f"Error de conexión con el servidor: {str(e)}. Por favor, inténtalo más tarde.", "danger")
        return render_template('productos.html', productos=[])

@app.route('/contactanos')
def contactanos():
    return render_template('contactanos.html')
    
@app.route('/conocenos')
def conocenos():
    return render_template('conocenos.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            # Determinar si es login de admin o cliente
            username = request.form['username']
            password = request.form['password']
            
            # Datos para la autenticación
            data = {
                "username": username,
                "password": password
            }
            
            response = requests.post(f"{API_URL}/token", data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                session['access_token'] = token_data['access_token']
                session['token_type'] = token_data['token_type']
                session['username'] = username
                
                # Obtener información del usuario
                headers = {"Authorization": f"Bearer {token_data['access_token']}"}
                user_response = requests.get(f"{API_URL}/usuarios/me", headers=headers)
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    session['user_id'] = user_data.get('id')
                    session['user_name'] = user_data.get('nombre', username)
                
                # Guardar tipo de usuario y ID en la sesión
                if username == 'admin':
                    session['user_type'] = 'admin'
                    flash("Inicio de sesión como administrador exitoso", "success")
                    return redirect(url_for('admin_dashboard'))
                else:
                    session['user_type'] = 'cliente'
                    
                    # Si no tenemos el user_id, intentar obtenerlo por nombre de usuario
                    if not session.get('user_id'):
                        try:
                            clientes_response = requests.get(f"{API_URL}/clientes/", headers=headers)
                            if clientes_response.status_code == 200:
                                clientes = clientes_response.json()
                                for cliente in clientes:
                                    if cliente.get('nombre') == username or cliente.get('email') == username:
                                        session['user_id'] = cliente.get('id')
                                        print(f"ID de cliente encontrado en login: {session['user_id']}")
                                        break
                        except Exception as e:
                            print(f"Error al buscar cliente por nombre: {str(e)}")
                    
                    flash("Inicio de sesión exitoso", "success")
                    return redirect(url_for('index'))
            else:
                flash("Credenciales incorrectas", "danger")
        except Exception as e:
            flash(f"Error de conexión: {str(e)}", "danger")
    
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        try:
            # Datos del nuevo cliente
            nuevo_cliente = {
                "nombre": request.form['nombre'],
                "email": request.form['email'],
                "contraseña": request.form['password'],
                "telefono": request.form['telefono'],
                "direccion": request.form['direccion']
            }
            
            headers = {"Content-Type": "application/json"}
            response = requests.post(f"{API_URL}/clientes/", json=nuevo_cliente, headers=headers)
            
            if response.status_code == 200:
                flash("Registro exitoso. Por favor inicie sesión", "success")
                return redirect(url_for('login'))
            else:
                error_msg = response.json().get('detail', 'Error desconocido')
                flash(f"Error en el registro: {error_msg}", "danger")
        except Exception as e:
            flash(f"Error de conexión: {str(e)}", "danger")
    
    return render_template('registro.html')

@app.route('/producto/<int:producto_id>')
def detalle_producto(producto_id):
    try:
        response = requests.get(f"{API_URL}/productos/{producto_id}")
        if response.status_code == 200:
            producto = response.json()
            return render_template('detalle_producto.html', producto=producto)
        else:
            flash("El producto solicitado no existe o ha sido eliminado. Por favor, vuelve a la lista de productos.", "warning")
            return redirect(url_for('productos'))
    except Exception as e:
        flash(f"Error de conexión con el servidor: {str(e)}. Por favor, inténtalo más tarde.", "danger")
        return redirect(url_for('productos'))

@app.route('/pedidos')
def mis_pedidos():
    if 'access_token' not in session:
        flash("Debe iniciar sesión para ver sus pedidos", "warning")
        return redirect(url_for('login'))
    
    try:
        headers = {"Authorization": f"{session['token_type']} {session['access_token']}"}
        response = requests.get(f"{API_URL}/pedidos/", headers=headers)
        
        if response.status_code == 200:
            pedidos = response.json()
            return render_template('mis_pedidos.html', pedidos=pedidos)
        else:
            flash("Error al obtener los pedidos", "danger")
            return redirect(url_for('index'))
    except Exception as e:
        flash(f"Error de conexión: {str(e)}", "danger")
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    flash("Ha cerrado sesión correctamente", "success")
    return redirect(url_for('index'))

# Rutas del carrito y checkout
@app.route('/carrito')
def carrito():
    if 'access_token' not in session:
        flash('Debes iniciar sesión para ver el carrito', 'warning')
        return redirect(url_for('login'))
    
    if 'carrito' not in session:
        session['carrito'] = {}
    
    try:
        productos_carrito = []
        total = 0
        
        # Obtener detalles de cada producto en el carrito
        for producto_id, cantidad in session['carrito'].items():
            response = requests.get(f"{API_URL}/productos/{producto_id}")
            if response.status_code == 200:
                producto = response.json()
                producto['cantidad'] = cantidad
                producto['subtotal'] = producto['precio'] * cantidad
                productos_carrito.append(producto)
                total += producto['subtotal']
        
        return render_template('carrito.html', productos=productos_carrito, total=total)
    except Exception as e:
        flash(f"Error al cargar el carrito: {str(e)}", "danger")
        return render_template('carrito.html', productos=[], total=0)

@app.route('/agregar-al-carrito', methods=['POST'])
def agregar_al_carrito():
    if 'access_token' not in session:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión'})
    
    try:
        data = request.get_json()
        producto_id = str(data.get('producto_id'))
        
        if 'carrito' not in session:
            session['carrito'] = {}
        
        if producto_id in session['carrito']:
            session['carrito'][producto_id] += 1
        else:
            session['carrito'][producto_id] = 1
        
        session.modified = True
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/actualizar-carrito', methods=['POST'])
def actualizar_carrito():
    if 'access_token' not in session:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión'})
    
    try:
        data = request.get_json()
        producto_id = str(data.get('producto_id'))
        cantidad = int(data.get('cantidad'))
        
        if cantidad <= 0:
            if producto_id in session['carrito']:
                del session['carrito'][producto_id]
        else:
            session['carrito'][producto_id] = cantidad
        
        session.modified = True
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/eliminar-del-carrito', methods=['POST'])
def eliminar_del_carrito():
    if 'access_token' not in session:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión'})
    
    try:
        data = request.get_json()
        producto_id = str(data.get('producto_id'))
        
        if producto_id in session['carrito']:
            del session['carrito'][producto_id]
            session.modified = True
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'access_token' not in session:
        flash('Debes iniciar sesión para realizar un pedido', 'warning')
        return redirect(url_for('login'))
    
    if 'carrito' not in session or not session['carrito']:
        flash('Tu carrito está vacío', 'warning')
        return redirect(url_for('productos'))
    
    try:
        productos_carrito = []
        total = 0
        
        # Obtener detalles de los productos para mostrar en el checkout
        for producto_id, cantidad in session['carrito'].items():
            response = requests.get(f"{API_URL}/productos/{producto_id}")
            if response.status_code == 200:
                producto = response.json()
                producto['cantidad'] = cantidad
                producto['subtotal'] = producto['precio'] * cantidad
                productos_carrito.append(producto)
                total += producto['subtotal']
        
        if request.method == 'POST':
            # Verificar que todos los campos requeridos estén presentes
            required_fields = ['direccion', 'telefono', 'email']
            for field in required_fields:
                if not request.form.get(field):
                    flash(f'El campo {field} es requerido', 'danger')
                    return redirect(url_for('checkout'))
            
            # Crear el pedido
            productos_pedido = []
            total = 0
            
            # Verificar stock y obtener información actualizada de productos
            headers = {"Authorization": f"{session['token_type']} {session['access_token']}"}
            
            for producto_id, cantidad in session['carrito'].items():
                response = requests.get(f"{API_URL}/productos/{producto_id}", headers=headers)
                if response.status_code == 200:
                    producto = response.json()
                    if producto['stock'] < cantidad:
                        flash(f'No hay suficiente stock de {producto["nombre"]}', 'danger')
                        return redirect(url_for('carrito'))
                    
                    subtotal = float(producto['precio']) * int(cantidad)
                    productos_pedido.append({
                        'producto_id': int(producto_id),
                        'cantidad': int(cantidad),
                        'precio_unitario': float(producto['precio']),
                        'subtotal': float(subtotal)
                    })
                    total += subtotal
                else:
                    flash(f'Error al verificar el producto con ID {producto_id}', 'danger')
                    return redirect(url_for('carrito'))
            
            # Obtener el ID del cliente
            try:
                headers = {"Authorization": f"{session['token_type']} {session['access_token']}"}
                # Verificar si el token está presente
                if not session.get('access_token') or not session.get('token_type'):
                    flash("Token de sesión no válido o expirado. Por favor, inicia sesión nuevamente.", "danger")
                    return redirect(url_for('login'))
                
                # Usar el user_id almacenado en la sesión durante el login
                cliente_id = session.get('user_id')
                
                # Si no tenemos el ID en la sesión pero tenemos el nombre/email, buscar en la lista de clientes
                if not cliente_id and 'username' in session:
                    try:
                        print("Intentando obtener el ID del usuario por nombre/email (comparación robusta)")
                        headers = {"Authorization": f"{session['token_type']} {session['access_token']}"}
                        clientes = []  # Inicializar la variable clientes
                        clientes_response = requests.get(f"{API_URL}/clientes/", headers=headers)
                        if clientes_response.status_code == 200:
                            clientes = clientes_response.json()
                            username_session = session['username'].strip().lower()
                            print(f"Username en sesión: {username_session}")
                            for cliente in clientes:
                                nombre_cliente = str(cliente.get('nombre', '')).strip().lower()
                                email_cliente = str(cliente.get('email', '')).strip().lower()
                                print(f"Comparando con cliente - Nombre: {nombre_cliente}, Email: {email_cliente}")
                                if username_session == nombre_cliente or username_session == email_cliente:
                                    cliente_id = cliente.get('id')
                                    print(f"Cliente encontrado: {cliente_id}")
                                    session['user_id'] = cliente_id
                                    break
                        if not cliente_id:
                            print("No se encontró el usuario en la base de datos. username:", session['username'])
                            print("Clientes disponibles:", clientes)
                            flash("No se pudo encontrar tu usuario en la base de datos. Por favor, contacta al administrador.", "danger")
                            return redirect(url_for('checkout'))
                    except Exception as e:
                        print(f"Error al buscar cliente por nombre/email: {str(e)}")
                        flash(f"Error al buscar tu usuario: {str(e)}", "danger")
                        return redirect(url_for('checkout'))
                
                print("ID del cliente usado para el pedido:", cliente_id)
                if not cliente_id:
                    flash("No se pudo obtener tu ID de cliente. Por favor, contacta al administrador.", "danger")
                    return redirect(url_for('checkout'))
            except Exception as e:
                flash(f"Error al obtener información del usuario: {str(e)}", "danger")
                return redirect(url_for('checkout'))
            
            # Datos del pedido con la estructura correcta
            # Calcular el total del primer producto
            total_primer_producto = productos_pedido[0]['precio_unitario'] * productos_pedido[0]['cantidad']
            
            pedido_data = {
                'cliente_id': cliente_id,
                'producto_id': productos_pedido[0]['producto_id'],  # Para el primer producto
                'cantidad': productos_pedido[0]['cantidad'],
                'precio_unitario': productos_pedido[0]['precio_unitario'],
                'total': float(total_primer_producto),  # Agregando el campo total requerido
                'direccion': request.form['direccion'],
                'telefono': request.form['telefono'],
                'email': request.form['email'],
                'estado': 'pendiente'
            }
            
            headers = {
                'Authorization': f"{session['token_type']} {session['access_token']}",
                'Content-Type': 'application/json'
            }
            
            # Imprimir datos para debugging
            print("Enviando pedido:", pedido_data)
            
            try:
                # Crear un pedido para cada producto en el carrito
                for producto in productos_pedido:
                    # Calcular el total del producto (precio unitario × cantidad)
                    total_producto = producto['precio_unitario'] * producto['cantidad']
                    
                    pedido_item = {
                        'cliente_id': cliente_id,
                        'producto_id': producto['producto_id'],
                        'cantidad': producto['cantidad'],
                        'precio_unitario': producto['precio_unitario'],
                        'total': float(total_producto),  # Convertir a float para asegurar la serialización
                        'direccion': request.form['direccion'],
                        'telefono': request.form['telefono'],
                        'email': request.form['email'],
                        'estado': 'pendiente'
                    }
                    
                    print(f"Enviando pedido para producto {producto['producto_id']}:", pedido_item)
                    
                    response = requests.post(
                        f"{API_URL}/pedidos/", 
                        json=pedido_item, 
                        headers=headers
                    )
                    
                    if response.status_code != 200:
                        error_msg = response.json().get('detail', 'Error desconocido en el servidor')
                        flash(f'Error al procesar el producto {producto["producto_id"]}: {error_msg}', 'danger')
                        print("Error response:", response.text)
                        return redirect(url_for('checkout'))
                
                # Si todos los pedidos se procesaron correctamente
                session.pop('carrito', None)
                flash('¡Pedido realizado con éxito! Te notificaremos cuando esté en camino.', 'success')
                return redirect(url_for('mis_pedidos'))
            except requests.exceptions.RequestException as e:
                flash(f"Error de conexión: {str(e)}", "danger")
                return redirect(url_for('checkout'))
            except Exception as e:
                flash(f"Error inesperado: {str(e)}", "danger")
                return redirect(url_for('checkout'))
        
        # Si es GET o hubo error, mostrar la página de checkout
        return render_template('checkout.html', productos=productos_carrito, total=total)
    
    except Exception as e:
        flash(f"Error al cargar el checkout: {str(e)}", "danger")
        return redirect(url_for('carrito'))

# Rutas del panel de administración
@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

@app.route('/admin/productos', methods=['GET'])
@admin_required
def admin_productos():
    try:
        headers = {"Authorization": f"{session['token_type']} {session['access_token']}"}
        response = requests.get(f"{API_URL}/productos/", headers=headers)
        
        if response.status_code == 200:
            productos = response.json()
            return render_template('admin/productos.html', productos=productos)
        else:
            flash("Error al obtener los productos", "danger")
            return redirect(url_for('admin_dashboard'))
    except Exception as e:
        flash(f"Error de conexión: {str(e)}", "danger")
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/productos/nuevo', methods=['GET', 'POST'])
@admin_required
def admin_nuevo_producto():
    if request.method == 'POST':
        try:
            # ===== GESTIÓN DE IMÁGENES DE PRODUCTOS =====
            # 1. Verificamos si el usuario ha enviado una imagen en el formulario
            if 'imagen' not in request.files:
                flash('No se ha seleccionado ninguna imagen', 'danger')
                return redirect(request.url)
            
            # 2. Obtenemos el archivo de imagen del formulario
            imagen = request.files['imagen']
            if imagen.filename == '':
                flash('No se ha seleccionado ninguna imagen', 'danger')
                return redirect(request.url)
            
            # 3. Procesamos la imagen si es válida
            if imagen and allowed_file(imagen.filename):
                # 4. Generamos un nombre de archivo seguro para evitar problemas de seguridad
                filename = secure_filename(imagen.filename)
                
                # 5. Creamos la carpeta de destino si no existe
                # La ruta será: frontend/static/img/productos/
                os.makedirs(os.path.join(app.static_folder, 'img', 'productos'), exist_ok=True)
                
                # 6. Guardamos la imagen en el servidor
                imagen_path = os.path.join(app.static_folder, 'img', 'productos', filename)
                imagen.save(imagen_path)
                
                # Crear el producto con la URL de la imagen
                nuevo_producto = {
                    "nombre": request.form['nombre'],
                    "precio": float(request.form['precio']),
                    "stock": int(request.form['stock']),
                    "descripcion": request.form['descripcion'],
                    "imagen_url": f"img/productos/{filename}",
                    "activo": True
                }
                
                headers = {
                    "Authorization": f"{session['token_type']} {session['access_token']}",
                    "Content-Type": "application/json"
                }
                
                response = requests.post(
                    f"{API_URL}/productos/", 
                    json=nuevo_producto,
                    headers=headers
                )
            
            if response.status_code == 200:
                flash("¡Producto creado exitosamente! El producto ya está disponible para los clientes.", "success")
                return redirect(url_for('admin_productos'))
            else:
                error_msg = response.json().get('detail', 'Error desconocido')
                flash(f"Error al crear producto: {error_msg}. Por favor, revisa los datos e inténtalo de nuevo.", "danger")
        except Exception as e:
            flash(f"Error en la comunicación con el servidor: {str(e)}. Por favor, inténtalo más tarde.", "danger")
    
    return render_template('admin/nuevo_producto.html')

@app.route('/admin/productos/editar/<int:producto_id>', methods=['GET', 'POST'])
@admin_required
def admin_editar_producto(producto_id):
    headers = {"Authorization": f"{session['token_type']} {session['access_token']}"}
    
    if request.method == 'POST':
        try:
            # Preparamos los datos del producto
            producto_actualizado = {
                "nombre": request.form['nombre'],
                "precio": float(request.form['precio']),
                "stock": int(request.form['stock']),
                "descripcion": request.form['descripcion'],
                "activo": True
            }
            
            # ===== ACTUALIZACIÓN DE IMÁGENES DE PRODUCTOS =====
            # Solo procesamos la imagen si el usuario ha subido una nueva
            if 'imagen' in request.files and request.files['imagen'].filename != '':
                imagen = request.files['imagen']
                if allowed_file(imagen.filename):
                    # 1. Generamos un nombre seguro para la imagen
                    filename = secure_filename(imagen.filename)
                    
                    # 2. Creamos la carpeta de destino si no existe
                    # La ruta será: frontend/static/img/productos/
                    os.makedirs(os.path.join(app.static_folder, 'img', 'productos'), exist_ok=True)
                    
                    # 3. Guardamos la imagen en el servidor
                    imagen_path = os.path.join(app.static_folder, 'img', 'productos', filename)
                    imagen.save(imagen_path)
                    
                    # 4. Actualizamos la URL de la imagen en la base de datos
                    # Esta URL es relativa a la carpeta static
                    producto_actualizado["imagen_url"] = f"img/productos/{filename}"
            
            headers["Content-Type"] = "application/json"
            
            response = requests.put(
                f"{API_URL}/productos/{producto_id}",
                json=producto_actualizado,
                headers=headers
            )
            
            if response.status_code == 200:
                flash("Producto actualizado exitosamente", "success")
                return redirect(url_for('admin_productos'))
            else:
                error_msg = response.json().get('detail', 'Error desconocido')
                flash(f"Error al actualizar producto: {error_msg}. Por favor, revisa los datos e inténtalo de nuevo.", "danger")
        except Exception as e:
            flash(f"Error de comunicación con el servidor: {str(e)}. Por favor, inténtalo más tarde.", "danger")
    
    # Obtener datos del producto
    try:
        response = requests.get(f"{API_URL}/productos/{producto_id}", headers=headers)
        if response.status_code == 200:
            producto = response.json()
            return render_template('admin/editar_producto.html', producto=producto)
        else:
            flash("Producto no encontrado", "danger")
            return redirect(url_for('admin_productos'))
    except Exception as e:
        flash(f"Error de conexión: {str(e)}", "danger")
        return redirect(url_for('admin_productos'))

@app.route('/admin/productos/eliminar/<int:producto_id>', methods=['POST'])
@admin_required
def admin_eliminar_producto(producto_id):
    try:
        headers = {"Authorization": f"{session['token_type']} {session['access_token']}"}
        response = requests.delete(f"{API_URL}/productos/{producto_id}", headers=headers)
        
        if response.status_code == 200:
            flash("Producto eliminado exitosamente de la base de datos", "success")
        else:
            error_msg = response.json().get('detail', 'Error desconocido')
            flash(f"Error al eliminar producto: {error_msg}. Por favor, inténtalo de nuevo o contacta al administrador.", "danger")
    except Exception as e:
        flash(f"Error de comunicación con el servidor: {str(e)}. Por favor, inténtalo más tarde.", "danger")
    
    return redirect(url_for('admin_productos'))

@app.route('/admin/pedidos')
@admin_required
def admin_pedidos():
    headers = {"Authorization": f"{session['token_type']} {session['access_token']}"}
    
    # Obtener el estado del filtro de la URL
    estado_filtro = request.args.get('estado', '')
    
    try:
        # Obtener todos los pedidos
        response = requests.get(f"{API_URL}/pedidos/", headers=headers)
        
        if response.status_code == 200:
            pedidos = response.json()
            
            # Aplicar filtro por estado si se ha seleccionado uno
            if estado_filtro:
                pedidos = [pedido for pedido in pedidos if pedido.get('estado') == estado_filtro]
            
            # Formatear las fechas para una visualización más amigable (hora Ecuador)
            from datetime import datetime, timedelta
            for pedido in pedidos:
                if 'fecha' in pedido and pedido['fecha']:
                    try:
                        # Convertir la fecha ISO a objeto datetime
                        fecha_obj = datetime.fromisoformat(pedido['fecha'].replace('Z', '+00:00'))
                        # Ajustar a hora de Ecuador (GMT-5)
                        fecha_ecuador = fecha_obj - timedelta(hours=5)
                        # Formatear la fecha de manera amigable
                        pedido['fecha_formateada'] = fecha_ecuador.strftime('%d/%m/%Y %H:%M')
                    except Exception as e:
                        print(f"Error al formatear fecha: {str(e)}")
                        pedido['fecha_formateada'] = pedido['fecha']
            
            return render_template('admin/pedidos.html', pedidos=pedidos, filtro_actual=estado_filtro)
        else:
            flash("Error al obtener los pedidos", "danger")
            return redirect(url_for('admin_dashboard'))
    except Exception as e:
        flash(f"Error de conexión: {str(e)}", "danger")
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/pedidos/actualizar/<int:pedido_id>', methods=['POST'])
@admin_required
def admin_actualizar_estado_pedido(pedido_id):
    try:
        nuevo_estado = request.form['estado']
        headers = {
            "Authorization": f"{session['token_type']} {session['access_token']}",
            "Content-Type": "application/json"
        }
        
        response = requests.put(
            f"{API_URL}/pedidos/{pedido_id}/estado", 
            json={"estado": nuevo_estado},
            headers=headers
        )
        
        if response.status_code == 200:
            flash(f"Estado del pedido actualizado a: {nuevo_estado}", "success")
        else:
            error_msg = response.json().get('detail', 'Error desconocido')
            flash(f"Error al actualizar estado: {error_msg}", "danger")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
    
    return redirect(url_for('admin_pedidos'))

@app.route('/admin/clientes')
@admin_required
def admin_clientes():
    try:
        headers = {"Authorization": f"{session['token_type']} {session['access_token']}"}
        
        # Obtener todos los clientes
        response = requests.get(f"{API_URL}/clientes/", headers=headers)
        
        if response.status_code == 200:
            clientes = response.json()
            
            # Formatear las fechas de registro para una visualización más amigable (hora Ecuador)
            from datetime import datetime, timedelta
            for cliente in clientes:
                if 'fecha_registro' in cliente and cliente['fecha_registro']:
                    try:
                        # Convertir la fecha ISO a objeto datetime
                        fecha_obj = datetime.fromisoformat(cliente['fecha_registro'].replace('Z', '+00:00'))
                        # Ajustar a hora de Ecuador (GMT-5)
                        fecha_ecuador = fecha_obj - timedelta(hours=5)
                        # Formatear la fecha de manera amigable
                        cliente['fecha_registro_formateada'] = fecha_ecuador.strftime('%d/%m/%Y %H:%M')
                    except Exception as e:
                        print(f"Error al formatear fecha de registro: {str(e)}")
                        cliente['fecha_registro_formateada'] = cliente['fecha_registro']
            
            # Para cada cliente, obtener sus pedidos
            for cliente in clientes:
                try:
                    pedidos_response = requests.get(
                        f"{API_URL}/pedidos/cliente/{cliente['id']}", 
                        headers=headers
                    )
                    
                    if pedidos_response.status_code == 200:
                        cliente['pedidos'] = pedidos_response.json()
                    else:
                        cliente['pedidos'] = []
                        print(f"Error al obtener pedidos del cliente {cliente['id']}: {pedidos_response.status_code}")
                except Exception as e:
                    cliente['pedidos'] = []
                    print(f"Error al procesar pedidos del cliente {cliente['id']}: {str(e)}")
            
            return render_template('admin/clientes.html', clientes=clientes)
        else:
            error_msg = response.json().get('detail', 'Error desconocido')
            flash(f"Error al obtener los clientes: {error_msg}", "danger")
            return redirect(url_for('admin_dashboard'))
    except Exception as e:
        flash(f"Error de conexión: {str(e)}", "danger")
        return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

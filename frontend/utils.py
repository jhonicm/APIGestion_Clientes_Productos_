# Funciones auxiliares para el carrito
def obtener_productos_carrito():
    productos_carrito = []
    total = 0
    
    if 'carrito' in session:
        for producto_id, cantidad in session['carrito'].items():
            try:
                response = requests.get(f"{API_URL}/productos/{producto_id}")
                if response.status_code == 200:
                    producto = response.json()
                    producto['cantidad'] = cantidad
                    producto['subtotal'] = producto['precio'] * cantidad
                    productos_carrito.append(producto)
                    total += producto['subtotal']
            except Exception as e:
                print(f"Error al obtener producto {producto_id}: {str(e)}")
    
    return productos_carrito, total

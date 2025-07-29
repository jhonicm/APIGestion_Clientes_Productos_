from sqlalchemy.orm import Session
from passlib.context import CryptContext
from . import models, schemas
from typing import Optional, List

# Configuración del hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Función para verificar contraseña
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Función para hashear contraseña
def get_password_hash(password):
    return pwd_context.hash(password)

# Funciones de autenticación
def authenticate_admin(db: Session, username: str, password: str):
    admin = db.query(models.Administrador).filter(models.Administrador.usuario == username).first()
    if not admin:
        return False
    if not verify_password(password, admin.contraseña):
        return False
    return admin

def authenticate_cliente(db: Session, email: str, password: str):
    cliente = db.query(models.Cliente).filter(models.Cliente.email == email).first()
    if not cliente:
        return False
    if not verify_password(password, cliente.contraseña):
        return False
    return cliente

# Operaciones CRUD para Productos
def get_productos(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Producto)
        .filter(models.Producto.activo == True)
        .order_by(models.Producto.id)  # <-- Agrega esta línea
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_producto(db: Session, producto_id: int):
    return db.query(models.Producto).filter(models.Producto.id == producto_id).first()

def create_producto(db: Session, producto: schemas.ProductoCreate):
    db_producto = models.Producto(
        nombre=producto.nombre,
        precio=producto.precio,
        stock=producto.stock,
        descripcion=producto.descripcion,
        imagen_url=producto.imagen_url,
        activo=producto.activo
    )
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto

def update_producto(db: Session, producto_id: int, producto: schemas.ProductoUpdate):
    db_producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if db_producto is None:
        return None
    
    # Actualizar solo los campos proporcionados
    update_data = producto.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_producto, key, value)
    
    db.commit()
    db.refresh(db_producto)
    return db_producto

def delete_producto(db: Session, producto_id: int):
    db_producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if db_producto is None:
        return None
    
    # Eliminamos físicamente el producto
    db.delete(db_producto)
    db.commit()
    return db_producto

# Operaciones CRUD para Clientes
def get_clientes(db: Session, skip: int = 0, limit: int = 100, order_by: str = None):
    query = db.query(models.Cliente).filter(models.Cliente.activo == True)
    if order_by:
        query = query.order_by(getattr(models.Cliente, order_by))
    return query.offset(skip).limit(limit).all()

def get_cliente(db: Session, cliente_id: int):
    return db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()

def get_cliente_by_email(db: Session, email: str):
    return db.query(models.Cliente).filter(models.Cliente.email == email).first()

def create_cliente(db: Session, cliente: schemas.ClienteCreate):
    hashed_password = get_password_hash(cliente.contraseña)
    db_cliente = models.Cliente(
        nombre=cliente.nombre,
        email=cliente.email,
        contraseña=hashed_password,
        telefono=cliente.telefono,
        direccion=cliente.direccion,
        activo=cliente.activo
    )
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

# Operaciones CRUD para Pedidos
def get_pedidos(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    estado: Optional[str] = None,
    cliente_id: Optional[int] = None
):
    try:
        print(f"Consultando pedidos con params: estado={estado}, cliente_id={cliente_id}")
        
        # Usar join para cargar las relaciones cliente y producto automáticamente
        query = db.query(models.Pedido).join(
            models.Cliente, models.Pedido.cliente_id == models.Cliente.id
        ).join(
            models.Producto, models.Pedido.producto_id == models.Producto.id
        )
        
        if estado:
            query = query.filter(models.Pedido.estado == estado)
        
        if cliente_id:
            query = query.filter(models.Pedido.cliente_id == cliente_id)
        
        # Ordenar por fecha de creación, más recientes primero
        query = query.order_by(models.Pedido.fecha.desc())
        
        result = query.offset(skip).limit(limit).all()
        print(f"Pedidos encontrados en BD: {len(result)}")
        return result
    except Exception as e:
        print(f"Error en get_pedidos: {e}")
        # Devolver una lista vacía en caso de error para evitar errores en cascada
        return []

def get_pedido(db: Session, pedido_id: int):
    try:
        print(f"Consultando pedido con ID: {pedido_id}")
        
        # Usar join para cargar las relaciones cliente y producto automáticamente
        pedido = db.query(models.Pedido).join(
            models.Cliente, models.Pedido.cliente_id == models.Cliente.id
        ).join(
            models.Producto, models.Pedido.producto_id == models.Producto.id
        ).filter(
            models.Pedido.id == pedido_id
        ).first()
        
        print(f"Pedido encontrado: {pedido is not None}")
        return pedido
    except Exception as e:
        print(f"Error en get_pedido: {e}")
        return None

def create_pedido(db: Session, pedido: schemas.PedidoCreate):
    # Verificar stock
    producto = db.query(models.Producto).filter(models.Producto.id == pedido.producto_id).first()
    if not producto or producto.stock < pedido.cantidad:
        return None
    
    # Crear el pedido
    db_pedido = models.Pedido(
        cliente_id=pedido.cliente_id,
        producto_id=pedido.producto_id,
        cantidad=pedido.cantidad,
        precio_unitario=pedido.precio_unitario,
        total=pedido.total,
        notas=pedido.notas
    )
    db.add(db_pedido)
    
    # Actualizar stock
    producto.stock -= pedido.cantidad
    
    db.commit()
    db.refresh(db_pedido)
    return db_pedido

def update_pedido_estado(db: Session, pedido_id: int, estado: str):
    db_pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if db_pedido is None:
        return None
    
    db_pedido.estado = estado
    db.commit()
    db.refresh(db_pedido)
    return db_pedido

# Operaciones para Administradores
def get_admin_by_username(db: Session, username: str):
    return db.query(models.Administrador).filter(models.Administrador.usuario == username).first()

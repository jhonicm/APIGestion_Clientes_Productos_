from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
import os

from app import models, database, schemas, crud

# Configurar la aplicación FastAPI
app = FastAPI(
    title="Radical K9 API",
    description="API para la gestión de productos, pedidos y clientes de Radical K9",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración JWT
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Inicializar la base de datos
models.Base.metadata.create_all(bind=database.engine)

# Función para crear token JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        user_type: str = payload.get("user_type")
        user_id: int = payload.get("user_id")
        
        print(f"Token decodificado: user_type={user_type}, user_id={user_id}, username={username}")
        token_data = {"username": username, "user_type": user_type, "user_id": user_id}
        
    except JWTError as e:
        print(f"Error al decodificar token: {e}")
        raise credentials_exception

    db = next(database.get_db())

    if user_type == "admin":
        print(f"Buscando administrador con usuario: {username}")
        user = crud.get_admin_by_username(db, username)
    else:  # cliente
        # Intentar obtener el cliente por su ID, que es más confiable
        print(f"Buscando cliente con ID: {user_id}")
        user = crud.get_cliente(db, cliente_id=user_id)
        
        if user is None:
            # Si no se encuentra por ID, intentar por email como fallback
            print(f"Cliente no encontrado por ID, intentando con email: {username}")
            user = crud.get_cliente_by_email(db, username)
    
    if user is None:
        print(f"Usuario no encontrado en la base de datos: user_type={user_type}, user_id={user_id}, username={username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo encontrar tu usuario en la base de datos. Por favor, contacta al administrador.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"Usuario encontrado exitosamente: {user}")
    return user

# Verificar si el usuario es administrador
def get_admin_user(current_user = Depends(get_current_user)):
    print(f"Verificando permisos de administrador para el usuario: {current_user}")
    if not hasattr(current_user, 'usuario'):  # Solo los administradores tienen campo 'usuario'
        print("El usuario no tiene permisos de administrador")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos suficientes"
        )
    print("Usuario verificado como administrador")
    return current_user

# Ruta para autenticación
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(database.get_db)):
    # Intentar autenticar como admin
    admin_user = crud.authenticate_admin(db, form_data.username, form_data.password)
    
    if admin_user:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": admin_user.usuario, "user_type": "admin", "user_id": admin_user.id},
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer", "user_type": "admin", "user_id": admin_user.id}
    
    # Si no es admin, intentar autenticar como cliente
    cliente = crud.authenticate_cliente(db, form_data.username, form_data.password)
    
    if cliente:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": cliente.email, "user_type": "cliente", "user_id": cliente.id},
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer", "user_type": "cliente", "user_id": cliente.id}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Usuario o contraseña incorrectos",
        headers={"WWW-Authenticate": "Bearer"},
    )

# Rutas para productos
@app.get("/productos/", response_model=list[schemas.Producto])
def get_productos(db = Depends(database.get_db), skip: int = 0, limit: int = 100):
    try:
        productos = crud.get_productos(db, skip=skip, limit=limit)
        return productos
    except Exception as e:
        print(f"Error al obtener productos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/productos/{producto_id}", response_model=schemas.Producto)
def get_producto(producto_id: int, db = Depends(database.get_db)):
    db_producto = crud.get_producto(db, producto_id)
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return db_producto

@app.post("/productos/", response_model=schemas.Producto)
def create_producto(producto: schemas.ProductoCreate, db = Depends(database.get_db), admin_user = Depends(get_admin_user)):
    return crud.create_producto(db=db, producto=producto)

@app.put("/productos/{producto_id}", response_model=schemas.Producto)
def update_producto(producto_id: int, producto: schemas.ProductoUpdate, db = Depends(database.get_db), admin_user = Depends(get_admin_user)):
    db_producto = crud.update_producto(db, producto_id, producto)
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return db_producto

@app.delete("/productos/{producto_id}", response_model=schemas.Producto)
def delete_producto(producto_id: int, db = Depends(database.get_db), admin_user = Depends(get_admin_user)):
    db_producto = crud.delete_producto(db, producto_id)
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return db_producto

# Rutas para clientes
@app.post("/clientes/", response_model=schemas.Cliente)
def create_cliente(cliente: schemas.ClienteCreate, db = Depends(database.get_db)):
    db_cliente = crud.get_cliente_by_email(db, email=cliente.email)
    if db_cliente:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    return crud.create_cliente(db=db, cliente=cliente)

@app.get("/clientes/", response_model=list[schemas.Cliente])
def get_clientes(
    db = Depends(database.get_db), 
    current_user = Depends(get_current_user),  # Cambiado de admin_user a current_user
    skip: int = 0, 
    limit: int = 100
):
    try:
        # Verificar si es administrador o cliente
        is_admin = hasattr(current_user, 'usuario')
        
        if is_admin:
            # Si es admin, puede ver todos los clientes
            print(f"Admin user accediendo a lista de clientes: {current_user}")
            clientes = crud.get_clientes(db, skip=skip, limit=limit, order_by="id")
        else:
            # Si es cliente, solo puede verse a sí mismo
            print(f"Cliente accediendo a su información: {current_user}")
            clientes = [current_user] if hasattr(current_user, 'id') else []
            
        print(f"Clientes obtenidos: {len(clientes)}")
        return clientes
    except Exception as e:
        print(f"Error en /clientes/: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.get("/clientes/{cliente_id}", response_model=schemas.Cliente)
def get_cliente(cliente_id: int, db = Depends(database.get_db), current_user = Depends(get_current_user)):
    # Verificar que sea administrador o el propio cliente
    is_admin = hasattr(current_user, 'usuario')
    is_same_client = hasattr(current_user, 'id') and current_user.id == cliente_id
    
    if not (is_admin or is_same_client):
        raise HTTPException(status_code=403, detail="No tiene permisos para ver este cliente")
    
    db_cliente = crud.get_cliente(db, cliente_id=cliente_id)
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return db_cliente

# Rutas para pedidos
@app.post("/pedidos/", response_model=schemas.Pedido)
def create_pedido(pedido: schemas.PedidoCreate, db = Depends(database.get_db), current_user = Depends(get_current_user)):
    try:
        # Verificar que sea administrador o el propio cliente
        is_admin = hasattr(current_user, 'usuario')
        print(f"Usuario creando pedido: {current_user}, es_admin: {is_admin}")
        print(f"Datos del pedido recibido: {pedido}")
        
        # Si es cliente, asegurarnos de que el cliente_id del pedido sea el del usuario autenticado
        if not is_admin:
            # Sobreescribir el cliente_id del pedido con el del usuario autenticado para evitar confusiones
            if hasattr(current_user, 'id'):
                print(f"Sobreescribiendo cliente_id del pedido: {pedido.cliente_id} -> {current_user.id}")
                pedido.cliente_id = current_user.id
            else:
                print(f"Error: El usuario actual no tiene ID: {current_user}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="Error de autenticación. Por favor, vuelve a iniciar sesión."
                )
        
        # Si es admin, verificar que exista el cliente para el que se está creando el pedido
        elif pedido.cliente_id:
            cliente = crud.get_cliente(db, cliente_id=pedido.cliente_id)
            if not cliente:
                print(f"Cliente con ID {pedido.cliente_id} no encontrado")
                raise HTTPException(status_code=404, detail=f"Cliente con ID {pedido.cliente_id} no encontrado")
        
        # Verificar si el producto existe y tiene suficiente stock
        producto = crud.get_producto(db, pedido.producto_id)
        if not producto:
            print(f"Producto con ID {pedido.producto_id} no encontrado")
            raise HTTPException(status_code=404, detail=f"Producto con ID {pedido.producto_id} no encontrado")
            
        if producto.stock < pedido.cantidad:
            print(f"Stock insuficiente: solicitado {pedido.cantidad}, disponible {producto.stock}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Stock insuficiente. Solicitado: {pedido.cantidad}, Disponible: {producto.stock}"
            )
            
        # Crear el pedido
        print(f"Creando pedido: cliente_id={pedido.cliente_id}, producto_id={pedido.producto_id}, cantidad={pedido.cantidad}")
        resultado = crud.create_pedido(db=db, pedido=pedido)
        
        if not resultado:
            print("Error desconocido al crear el pedido")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="No se pudo crear el pedido. Verifica que haya suficiente stock disponible."
            )
        
        print(f"Pedido creado exitosamente: {resultado.id}")
        return resultado
    except Exception as e:
        print(f"Error no controlado al crear pedido: {str(e)}")
        raise

@app.get("/pedidos/", response_model=list[schemas.Pedido])
def get_pedidos(
    db = Depends(database.get_db), 
    current_user = Depends(get_current_user),
    skip: int = 0, 
    limit: int = 100,
    estado: Optional[str] = None,
    cliente_id: Optional[int] = None
):
    try:
        # Verificar permisos
        is_admin = hasattr(current_user, 'usuario')
        print(f"Usuario consultando pedidos: {current_user}, es_admin: {is_admin}")
        
        if not is_admin and cliente_id is not None and cliente_id != current_user.id:
            print(f"Intento de acceso no autorizado: cliente_id={cliente_id}, current_user.id={current_user.id}")
            raise HTTPException(status_code=403, detail="No tiene permisos para ver pedidos de otros clientes")
        
        if not is_admin:
            # Si es cliente, solo puede ver sus propios pedidos
            if hasattr(current_user, 'id'):
                cliente_id = current_user.id
                print(f"Cliente consultando sus pedidos, id: {cliente_id}")
            else:
                print(f"Error: El cliente no tiene ID: {current_user}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="Error de autenticación. Por favor, vuelve a iniciar sesión."
                )
        
        # Realizar la consulta a la base de datos
        pedidos = crud.get_pedidos(db, skip=skip, limit=limit, estado=estado, cliente_id=cliente_id)
        print(f"Pedidos encontrados: {len(pedidos)}")
        
        # Asegurar que los datos de relaciones (cliente y producto) estén cargados correctamente
        result = []
        for pedido in pedidos:
            # Cargar manualmente la información del cliente y producto si es necesario
            if pedido.cliente_id and not pedido.cliente:
                pedido.cliente = db.query(models.Cliente).filter(models.Cliente.id == pedido.cliente_id).first()
            
            if pedido.producto_id and not pedido.producto:
                pedido.producto = db.query(models.Producto).filter(models.Producto.id == pedido.producto_id).first()
            
            result.append(pedido)
        
        print(f"Retornando {len(result)} pedidos procesados")
        return result
    except Exception as e:
        print(f"Error no controlado al obtener pedidos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener los pedidos: {str(e)}")

@app.get("/pedidos/{pedido_id}", response_model=schemas.Pedido)
def get_pedido(pedido_id: int, db = Depends(database.get_db), current_user = Depends(get_current_user)):
    try:
        print(f"Buscando pedido con ID: {pedido_id}")
        db_pedido = crud.get_pedido(db, pedido_id)
        
        if db_pedido is None:
            print(f"Pedido con ID {pedido_id} no encontrado")
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        # Verificar permisos
        is_admin = hasattr(current_user, 'usuario')
        is_client_owner = hasattr(current_user, 'id') and current_user.id == db_pedido.cliente_id
        
        print(f"Verificando permisos - Es admin: {is_admin}, Es dueño: {is_client_owner}")
        
        if not (is_admin or is_client_owner):
            print(f"Usuario {current_user} no tiene permisos para ver el pedido {pedido_id}")
            raise HTTPException(status_code=403, detail="No tiene permisos para ver este pedido")
        
        # Cargar manualmente la información del cliente y producto si es necesario
        if db_pedido.cliente_id and not db_pedido.cliente:
            db_pedido.cliente = db.query(models.Cliente).filter(models.Cliente.id == db_pedido.cliente_id).first()
        
        if db_pedido.producto_id and not db_pedido.producto:
            db_pedido.producto = db.query(models.Producto).filter(models.Producto.id == db_pedido.producto_id).first()
        
        print(f"Retornando pedido: {db_pedido.id}")
        return db_pedido
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error no controlado al obtener el pedido {pedido_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener el pedido: {str(e)}")

@app.put("/pedidos/{pedido_id}/estado", response_model=schemas.Pedido)
def update_pedido_estado(
    pedido_id: int, 
    estado_update: schemas.PedidoEstadoUpdate, 
    db = Depends(database.get_db), 
    admin_user = Depends(get_admin_user)
):
    db_pedido = crud.get_pedido(db, pedido_id)
    if db_pedido is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    if db_pedido.estado in ["Entregado", "Cancelado"]:
        raise HTTPException(status_code=400, detail=f"No se puede cambiar el estado de un pedido {db_pedido.estado.lower()}")
    
    db_pedido = crud.update_pedido_estado(db, pedido_id, estado_update.estado)
    return db_pedido

# Ruta específica para obtener los pedidos de un cliente por su ID
@app.get("/pedidos/cliente/{cliente_id}", response_model=list[schemas.Pedido])
def get_pedidos_cliente(
    cliente_id: int,
    db = Depends(database.get_db),
    admin_user = Depends(get_admin_user),  # Solo los administradores pueden ver todos los pedidos de cualquier cliente
    skip: int = 0,
    limit: int = 100,
    estado: Optional[str] = None
):
    try:
        # Obtener los pedidos del cliente
        pedidos = crud.get_pedidos(db, skip=skip, limit=limit, estado=estado, cliente_id=cliente_id)
        return pedidos
    except Exception as e:
        print(f"Error al obtener pedidos del cliente {cliente_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al procesar la solicitud: {str(e)}")

# Endpoint para verificar el estado de salud de la API
@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

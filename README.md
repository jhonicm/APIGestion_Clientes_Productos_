# Radical K9 - Sistema de Gestión E-commerce

Este proyecto implementa un sistema completo de comercio electrónico para la gestión de productos, pedidos y clientes para una tienda de productos para perros especializada en equipo profesional de entrenamiento, rescate y trabajo. El sistema incluye tanto un backend robusto con API RESTful como un frontend interactivo para clientes y panel de administración.

## Funcionalidades


1. **Gestión de Productos**
   - Listado de todos los productos disponibles
   - Detalles de productos individuales
   - Crear, actualizar y eliminar productos (solo admin)
   - Control de stock

2. **Gestión de Clientes**
   - Registro de nuevos clientes
   - Consulta de información del cliente
   - Gestión de perfiles

3. **Gestión de Pedidos**
   - Creación de nuevos pedidos
   - Consulta de estado de pedidos
   - Filtrado por cliente y estado
   - Actualización del estado de pedidos (solo admin)

## Tecnologías utilizadas

### Backend
- **API REST**: FastAPI (Python)
- **Base de datos**: SQL Server
- **Contenedorización**: Docker y Docker Compose
- **Seguridad**: JWT, Bcrypt para hashing de contraseñas
- **Mensajería**: Kafka para comunicación asíncrona entre servicios

### Frontend
- **Framework Web**: Flask (Python)
- **Interfaz de usuario**: HTML5, CSS3, Bootstrap 5
- **JavaScript**: Vanilla JS con fetch API para llamadas asíncronas
- **Plantillas**: Jinja2
- **Interactividad**: Formularios dinámicos y manejo de carrito de compras

## Características destacadas

- **Sistema de inventario en tiempo real**: Muestra a los clientes la disponibilidad exacta de productos
- **Carrito de compras persistente**: Los usuarios pueden añadir productos y continuar más tarde
- **Panel de administración completo**: Gestión de productos, clientes y pedidos
- **Diseño responsive**: Experiencia optimizada en dispositivos móviles y de escritorio
- **Manejo de imágenes**: Subida y gestión de imágenes de productos
- **Notificaciones**: Sistema de alertas para clientes y administradores
- **Múltiples métodos de pago**: Integración con diferentes opciones de pago (simulado)

## Estructura del Proyecto

```
radical_k9/
│
├── api/                  # Directorio del backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py       # Punto de entrada de la API
│   │   ├── database.py   # Configuración de la base de datos
│   │   ├── models.py     # Modelos SQLAlchemy
│   │   ├── schemas.py    # Esquemas Pydantic
│   │   └── crud.py       # Operaciones CRUD
│   │
│   ├── Dockerfile        # Dockerfile para el backend
│   └── requirements.txt  # Dependencias de Python
│
├── frontend/             # Aplicación web con Flask
│   ├── app.py            # Aplicación principal de Flask
│   ├── Dockerfile        # Dockerfile para el frontend
│   ├── requirements.txt  # Dependencias del frontend
│   ├── static/           # Archivos estáticos (CSS, JS, imágenes)
│   └── templates/        # Plantillas HTML con Jinja2
│       ├── admin/        # Plantillas del panel de administración
│       └── ...           # Otras plantillas
│
├── db/                   # Archivos relacionados con la base de datos
│   └── init/             
│       └── init.sql      # Script de inicialización de la base de datos
│
└── docker-compose.yml    # Configuración de Docker Compose
```


4. Accede a la aplicación:
   - **Frontend (Tienda)**: `http://localhost:5000`
   - **API Backend**: `http://localhost:8080`
   - **Documentación de la API**: `http://localhost:8080/docs`


## Endpoints principales de la API

- `/token` - Autenticación (POST)
- `/productos/` - Gestión de productos (GET, POST)
- `/productos/{id}` - Operaciones sobre un producto específico (GET, PUT, DELETE)
- `/clientes/` - Gestión de clientes (GET, POST)
- `/clientes/{id}` - Operaciones sobre un cliente específico (GET)
- `/pedidos/` - Gestión de pedidos (GET, POST)
- `/pedidos/{id}` - Operaciones sobre un pedido específico (GET)
- `/pedidos/{id}/estado` - Actualizar estado de un pedido (PUT)


## Autores

- **Jhon Israel Cordova Mosquera** - *Desarrollo completo* - [jhonicm](https://github.com/jhonicm)


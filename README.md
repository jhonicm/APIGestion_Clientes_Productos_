# Radical K9 - Sistema de Gestión E-commerce

Este proyecto implementa un sistema completo de comercio electrónico para la gestión de productos, pedidos y clientes para una tienda de productos para perros especializada en equipo profesional de entrenamiento, rescate y trabajo. El sistema incluye tanto un backend robusto con API RESTful como un frontend interactivo para clientes y panel de administración.

## Funcionalidades

1. **Autenticación y Autorización**
   - Sistema de login para clientes y administradores
   - Autenticación basada en JWT (JSON Web Tokens)
   - Diferentes niveles de permisos según el rol

2. **Gestión de Productos**
   - Listado de todos los productos disponibles
   - Detalles de productos individuales
   - Crear, actualizar y eliminar productos (solo admin)
   - Control de stock

3. **Gestión de Clientes**
   - Registro de nuevos clientes
   - Consulta de información del cliente
   - Gestión de perfiles

4. **Gestión de Pedidos**
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

## Cómo ejecutar el proyecto

1. Asegúrate de tener Docker y Docker Compose instalados

2. Clona el repositorio
   ```bash
   git clone https://github.com/jhonicm/radical_k9.git
   ```

3. Navega al directorio del proyecto
   ```bash
   cd radical_k9
   ```

4. Inicia los contenedores
   ```bash
   docker-compose up --build
   ```

5. Accede a la aplicación:
   - **Frontend (Tienda)**: `http://localhost:5000`
   - **API Backend**: `http://localhost:8000`
   - **Documentación de la API**: `http://localhost:8000/docs`

## Acceso al sistema

### Cliente de prueba
- **Usuario**: cliente@example.com
- **Contraseña**: password123

### Administrador de prueba
- **Usuario**: admin@example.com
- **Contraseña**: admin123

## Principales rutas del frontend

### Rutas públicas
- `/` - Página principal
- `/productos` - Catálogo de productos
- `/contactanos` - Información de la tienda y contacto
- `/login` - Inicio de sesión
- `/registro` - Registro de nuevos usuarios

### Rutas de cliente (requieren autenticación)
- `/carrito` - Carrito de compras
- `/checkout` - Proceso de compra
- `/mis-pedidos` - Historial de pedidos del cliente
- `/perfil` - Gestión del perfil de usuario

### Rutas de administración (requieren rol admin)
- `/admin/dashboard` - Panel principal de administración
- `/admin/productos` - Gestión de productos
- `/admin/pedidos` - Gestión de pedidos
- `/admin/clientes` - Gestión de clientes

## Endpoints principales de la API

- `/token` - Autenticación (POST)
- `/productos/` - Gestión de productos (GET, POST)
- `/productos/{id}` - Operaciones sobre un producto específico (GET, PUT, DELETE)
- `/clientes/` - Gestión de clientes (GET, POST)
- `/clientes/{id}` - Operaciones sobre un cliente específico (GET)
- `/pedidos/` - Gestión de pedidos (GET, POST)
- `/pedidos/{id}` - Operaciones sobre un pedido específico (GET)
- `/pedidos/{id}/estado` - Actualizar estado de un pedido (PUT)

## Capturas de pantalla

![Página principal](docs/screenshots/home.png)
![Catálogo de productos](docs/screenshots/productos.png)
![Panel de administración](docs/screenshots/admin.png)

## Autores

- **Jhon Carlos Mora** - *Desarrollo completo* - [jhonicm](https://github.com/jhonicm)

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE.md](LICENSE.md) para más detalles.

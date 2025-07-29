CREATE DATABASE GestionPedidos;
GO

USE GestionPedidos;
GO
-- Tabla de Productos
CREATE TABLE Productos (
    id INT PRIMARY KEY IDENTITY(1,1),
    nombre NVARCHAR(100) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    stock INT DEFAULT 0,
    descripcion NVARCHAR(500),
    imagen_url NVARCHAR(255),
    activo BIT DEFAULT 1,
    fecha_creacion DATETIME DEFAULT GETDATE()
);

-- Tabla de Clientes
CREATE TABLE Clientes (
    id INT PRIMARY KEY IDENTITY(1,1),
    nombre NVARCHAR(100) NOT NULL,
    email NVARCHAR(100) UNIQUE NOT NULL,
    contraseña NVARCHAR(255) NOT NULL,
    telefono NVARCHAR(20),
    direccion NVARCHAR(255),
    fecha_registro DATETIME DEFAULT GETDATE(),
    activo BIT DEFAULT 1
);

-- Tabla de Pedidos
CREATE TABLE Pedidos (
    id INT PRIMARY KEY IDENTITY(1,1),
    cliente_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT DEFAULT 1,
    precio_unitario DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    estado NVARCHAR(50) DEFAULT 'Pendiente',
    fecha DATETIME DEFAULT GETDATE(),
    notas NVARCHAR(500),
    FOREIGN KEY (cliente_id) REFERENCES Clientes(id),
    FOREIGN KEY (producto_id) REFERENCES Productos(id)
);

-- Tabla de Administradores
CREATE TABLE Administradores (
    id INT PRIMARY KEY IDENTITY(1,1),
    usuario NVARCHAR(50) UNIQUE NOT NULL,
    email NVARCHAR(100) UNIQUE NOT NULL,
    contraseña NVARCHAR(255) NOT NULL,
    nombre NVARCHAR(100) NOT NULL,
    activo BIT DEFAULT 1,
    fecha_creacion DATETIME DEFAULT GETDATE()
);

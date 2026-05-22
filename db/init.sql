CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    contrasena VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    cedula VARCHAR(20) NOT NULL UNIQUE,
    telefono VARCHAR(20),
    correo VARCHAR(100),
    usuario_id INT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS motos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    placa VARCHAR(10) NOT NULL UNIQUE,
    marca VARCHAR(50),
    modelo VARCHAR(50),
    anio INT,
    cliente_id INT,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

CREATE TABLE IF NOT EXISTS mantenimientos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    moto_id INT,
    fecha DATE NOT NULL,
    descripcion TEXT,
    repuestos TEXT,
    proximo_mantenimiento DATE,
    FOREIGN KEY (moto_id) REFERENCES motos(id)
);

INSERT INTO usuarios (usuario, contrasena, rol) VALUES
('admin', 'admin123', 'administrador'),
('cliente1', 'cliente123', 'cliente');

INSERT INTO clientes (nombre, cedula, telefono, correo, usuario_id) VALUES
('Cliente Demo', '123456789', '3001234567', 'cliente@demo.com', 2);

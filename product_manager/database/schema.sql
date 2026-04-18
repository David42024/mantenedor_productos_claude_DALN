-- ============================================================
-- Schema para Sistema de Gestión de Productos
-- PostgreSQL
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla principal de productos
CREATE TABLE IF NOT EXISTS productos (
    id              SERIAL PRIMARY KEY,
    sku             VARCHAR(50) UNIQUE NOT NULL,
    nombre          VARCHAR(200) NOT NULL,
    descripcion     TEXT,
    categoria       VARCHAR(100) NOT NULL,
    precio_compra   NUMERIC(12, 2) NOT NULL CHECK (precio_compra >= 0),
    precio_venta    NUMERIC(12, 2) NOT NULL CHECK (precio_venta >= 0),
    stock_actual    INTEGER NOT NULL DEFAULT 0 CHECK (stock_actual >= 0),
    stock_minimo    INTEGER NOT NULL DEFAULT 0 CHECK (stock_minimo >= 0),
    proveedor       VARCHAR(200),
    fecha_creacion          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    fecha_ultima_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_productos_categoria ON productos(categoria);
CREATE INDEX IF NOT EXISTS idx_productos_sku ON productos(sku);
CREATE INDEX IF NOT EXISTS idx_productos_stock ON productos(stock_actual);

-- Trigger para actualizar fecha_ultima_actualizacion automáticamente
CREATE OR REPLACE FUNCTION update_fecha_actualizacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_ultima_actualizacion = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_fecha ON productos;
CREATE TRIGGER trigger_update_fecha
    BEFORE UPDATE ON productos
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_actualizacion();

-- ============================================================
-- Datos de ejemplo para pruebas
-- ============================================================
INSERT INTO productos (sku, nombre, descripcion, categoria, precio_compra, precio_venta, stock_actual, stock_minimo, proveedor) VALUES
('ELEC-001', 'Laptop HP ProBook 450', 'Laptop profesional 15.6" Intel Core i7', 'Electrónica', 650.00, 950.00, 15, 5, 'HP Enterprise'),
('ELEC-002', 'Monitor LG 27" 4K', 'Monitor Ultra HD IPS 27 pulgadas', 'Electrónica', 280.00, 420.00, 8, 3, 'LG Electronics'),
('ELEC-003', 'Teclado Mecánico Logitech', 'Teclado inalámbrico retroiluminado', 'Electrónica', 45.00, 89.00, 3, 10, 'Logitech'),
('OFIC-001', 'Silla Ergonómica Premium', 'Silla de oficina con soporte lumbar ajustable', 'Mobiliario', 120.00, 245.00, 20, 5, 'OfficeMax'),
('OFIC-002', 'Escritorio Standing Desk', 'Escritorio regulable en altura eléctrico', 'Mobiliario', 350.00, 580.00, 4, 2, 'OfficeMax'),
('PAPE-001', 'Resma Papel A4 500 hojas', 'Papel bond blanco 75gr/m2', 'Papelería', 3.50, 6.50, 200, 50, 'Servicios Gráficos SA'),
('PAPE-002', 'Bolígrafos Pilot G2 (caja 12)', 'Bolígrafos gel retráctiles azul', 'Papelería', 8.00, 15.00, 45, 20, 'Pilot Corporation'),
('PAPE-003', 'Archivadores A4 (pack 10)', 'Archivadores palanca lomo ancho', 'Papelería', 12.00, 22.00, 2, 15, 'Avery Dennison'),
('TECH-001', 'Router WiFi 6 Asus', 'Router AX3000 dual band WiFi 6', 'Redes', 85.00, 145.00, 12, 4, 'Asus Networks'),
('TECH-002', 'Switch 24 Puertos Cisco', 'Switch administrable Gigabit 24 puertos', 'Redes', 180.00, 310.00, 6, 2, 'Cisco Systems'),
('TECH-003', 'Cable UTP Cat6 (caja 305m)', 'Cable de red categoría 6 LSZH', 'Redes', 55.00, 95.00, 8, 3, 'Belden'),
('ELEC-004', 'Impresora Epson EcoTank', 'Impresora multifuncional recargable', 'Electrónica', 130.00, 220.00, 5, 3, 'Epson'),
('ELEC-005', 'Auriculares Sony WH-1000XM5', 'Auriculares ANC premium inalámbricos', 'Electrónica', 220.00, 380.00, 1, 5, 'Sony'),
('OFIC-003', 'Lámpara LED de Escritorio', 'Lámpara con control táctil y USB', 'Mobiliario', 25.00, 48.00, 18, 8, 'Philips Lighting'),
('CONS-001', 'Café Molido Premium 1kg', 'Café arábico selecto tostado oscuro', 'Consumibles', 12.00, 22.00, 30, 15, 'Café del Norte'),
('CONS-002', 'Agua Mineral 20L bidón', 'Agua purificada para dispensador', 'Consumibles', 4.50, 8.00, 10, 5, 'AguaPura SAC'),
('TECH-004', 'UPS 1500VA APC', 'Sistema de alimentación ininterrumpida', 'Redes', 95.00, 165.00, 3, 2, 'APC by Schneider'),
('ELEC-006', 'Webcam Logitech C920', 'Cámara web Full HD 1080p', 'Electrónica', 55.00, 95.00, 0, 5, 'Logitech'),
('PAPE-004', 'Etiquetas Adhesivas (pack 100)', 'Etiquetas multiuso blancas A4', 'Papelería', 5.00, 9.50, 1, 10, 'Avery Dennison'),
('OFIC-004', 'Dispensador de Agua Fría/Caliente', 'Dispensador de bidón con compresor', 'Mobiliario', 140.00, 240.00, 2, 1, 'Aquaservice')
ON CONFLICT (sku) DO NOTHING;

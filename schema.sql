-- ====================================================================
-- HIMALAYAN PINK SALT OF PAKISTAN (KHEWRA) - DATABASE SCHEMA
-- Compatible with SQLite, PostgreSQL, and MySQL
-- ====================================================================

-- 1. PRODUCT CATEGORIES TABLE
CREATE TABLE IF NOT EXISTS categories (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. PRODUCTS CATALOG TABLE
CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(50) PRIMARY KEY,
    category_id VARCHAR(50) REFERENCES categories(id),
    name VARCHAR(150) NOT NULL,
    grain_size VARCHAR(50),
    standard_packaging VARCHAR(100),
    fob_price_per_ton_usd DECIMAL(10, 2),
    purity_percentage DECIMAL(4, 2) DEFAULT 98.20,
    description TEXT,
    icon_or_image VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. EXPORT INQUIRIES & RFQs (REQUEST FOR QUOTATION)
CREATE TABLE IF NOT EXISTS inquiries (
    id VARCHAR(50) PRIMARY KEY,
    reference_no VARCHAR(50) UNIQUE NOT NULL,
    buyer_name VARCHAR(100) NOT NULL,
    company_name VARCHAR(150),
    email VARCHAR(150),
    phone_whatsapp VARCHAR(50),
    product_name VARCHAR(150) NOT NULL,
    volume VARCHAR(100) NOT NULL,
    packaging VARCHAR(100) NOT NULL,
    destination_port VARCHAR(150) NOT NULL,
    incoterm VARCHAR(20) DEFAULT 'FOB Karachi',
    special_notes TEXT,
    status VARCHAR(30) DEFAULT 'new', -- 'new', 'in_review', 'quoted', 'negotiating', 'deal_won', 'closed'
    quoted_price_usd DECIMAL(12, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. BUYERS / CUSTOMER LEADS DIRECTORY
CREATE TABLE IF NOT EXISTS buyers (
    id VARCHAR(50) PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
    contact_person VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    phone VARCHAR(50),
    country VARCHAR(100),
    business_type VARCHAR(50), -- 'Wholesaler', 'Food Processor', 'Retail Chain', 'Spa Brand'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. SHIPMENTS / CONTRACT ORDERS
CREATE TABLE IF NOT EXISTS export_orders (
    id VARCHAR(50) PRIMARY KEY,
    inquiry_id VARCHAR(50) REFERENCES inquiries(id),
    buyer_id VARCHAR(50) REFERENCES buyers(id),
    container_count INT DEFAULT 1,
    container_size VARCHAR(20), -- '20ft FCL', '40ft FCL'
    total_metric_tons DECIMAL(10, 2) NOT NULL,
    total_amount_usd DECIMAL(12, 2) NOT NULL,
    payment_terms VARCHAR(100) DEFAULT '30% Advance T/T, 70% Against B/L',
    shipping_port VARCHAR(100) DEFAULT 'Karachi Port / Port Qasim',
    destination_port VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending_production', -- 'in_production', 'customs_cleared', 'shipped', 'delivered'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ====================================================================
-- SEED DATA (INITIAL KHEWRA PRODUCT CATALOG)
-- ====================================================================

INSERT INTO categories (id, name, description) VALUES
('edible', 'Edible Gourmet Salt', 'Food grade table and culinary salt crystals'),
('culinary', 'Cooking & Grilling Slabs', 'Solid rock salt slabs for searing and culinary presentation'),
('lamps', 'Hand-Carved Crystal Lamps', 'Ambient air-ionizing crystal lamps with rosewood base'),
('wellness', 'Spa & Bath Crystals', 'Detoxifying and balneotherapy mineral crystals'),
('animal', 'Agricultural Animal Licks', 'Mineral lick stones with hanging ropes for livestock');

INSERT INTO products (id, category_id, name, grain_size, standard_packaging, fob_price_per_ton_usd, purity_percentage, description, icon_or_image) VALUES
('prod-001', 'edible', 'Fine Table Pink Salt', '0.2–0.8mm', '25kg PP Woven Bags / Retail Jars', 180.00, 98.50, 'Micro-milled pure pink salt for food seasoning and table use.', '🧂'),
('prod-002', 'edible', 'Coarse Pink Salt Crystals', '2.0–5.0mm', '50kg Bags / Grinder Pouches', 160.00, 98.40, 'Translucent gemstone-like granules for refillable grinders.', '✨'),
('prod-003', 'culinary', 'Pink Salt Grilling Slabs', '8x8x2 inches', 'Individual export cartons', 450.00, 98.80, 'Solid salt blocks for searing steaks and seafood at 450°F.', '🥩'),
('prod-004', 'lamps', 'Natural Handcrafted Salt Lamps', '2kg to 5kg', 'Export master cartons with UL fittings', 650.00, 98.00, 'Hand-chiseled lamps with ambient amber ionization glow.', '💡'),
('prod-005', 'wellness', 'Himalayan Bath & Therapy Salts', '1.0–3.0mm', '25kg Pails / Retail Pouches', 210.00, 98.20, 'Pure bath crystals for skin detox and halotherapy spas.', '🛁'),
('prod-006', 'animal', 'Organic Animal Lick Salt with Rope', '3kg to 5kg block', 'Shrink-wrapped with hanging rope', 140.00, 97.90, 'Solid mineral lick stones for cattle and horses.', '🐎');

-- SAMPLE INITIAL INQUIRY (FOR DEMO/TESTING)
INSERT INTO inquiries (id, reference_no, buyer_name, company_name, email, phone_whatsapp, product_name, volume, packaging, destination_port, status) VALUES
('inq-101', 'RFQ-2026-001', 'Alexander Vance', 'EuroSpice Global B.V.', 'avance@eurospice.nl', '+31 20 123 4567', 'Fine Table Pink Salt', '20ft FCL Container (~25 MT)', 'Bulk 25kg PP Woven Bags', 'Port of Rotterdam, Netherlands', 'new');

"""
Himalayan Pink Salt of Pakistan - Backend Database Server (SQLite + REST API)
Run with: python server.py
Serves static frontend and provides REST endpoints for inquiries and products.
"""

import http.server
import json
import sqlite3
import os
import urllib.parse
from datetime import datetime

PORT = 8080
DB_FILE = os.path.join(os.path.dirname(__file__), "pink_salt.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 1. Inquiries Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inquiries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reference_no TEXT UNIQUE,
        buyer_name TEXT,
        company_name TEXT,
        email TEXT,
        phone_whatsapp TEXT,
        product_name TEXT,
        volume TEXT,
        packaging TEXT,
        destination_port TEXT,
        special_notes TEXT,
        status TEXT DEFAULT 'new',
        created_at TEXT
    )
    """)
    
    # 2. Products Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        grain_size TEXT,
        standard_packaging TEXT,
        fob_price_usd REAL,
        description TEXT,
        icon TEXT,
        is_active INTEGER DEFAULT 1
    )
    """)
    
    # Seed sample products if empty
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ("Fine Table Pink Salt", "edible", "0.2–0.8mm", "25kg PP Bags / Jars", 180.0, "Micro-milled pure pink salt for food seasoning.", "🧂"),
            ("Coarse Pink Salt Crystals", "edible", "2.0–5.0mm", "50kg Bags / Pouches", 160.0, "Translucent crystals for refillable salt grinders.", "✨"),
            ("Pink Salt Grilling Slabs", "culinary", "8x8x2 inches", "Cartons", 450.0, "Solid crystal block for searing steaks & seafood.", "🥩"),
            ("Natural Handcrafted Salt Lamps", "lamps", "2kg to 5kg", "Carton with UL fittings", 650.0, "Hand-chiseled lamps with ambient amber glow.", "💡"),
            ("Himalayan Bath & Spa Salts", "wellness", "1.0–3.0mm", "25kg Pails / Drums", 210.0, "Pure bath crystals for detox & halotherapy.", "🛁"),
            ("Organic Animal Lick Salt with Rope", "animal", "3kg to 5kg", "Shrink-wrapped with rope", 140.0, "Solid mineral lick blocks for livestock & horses.", "🐎")
        ]
        cursor.executemany("""
        INSERT INTO products (name, category, grain_size, standard_packaging, fob_price_usd, description, icon)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, sample_products)
        
    conn.commit()
    conn.close()

class SaltApiHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE, PUT')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        
        # API: Get Inquiries
        if url.path == "/api/inquiries":
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM inquiries ORDER BY id DESC")
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(rows).encode("utf-8"))
            return

        # API: Get Products
        if url.path == "/api/products":
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE is_active = 1")
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(rows).encode("utf-8"))
            return

        # Serve static files (HTML, CSS, JS)
        return super().do_GET()

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(post_data) if post_data else {}
        except Exception:
            data = {}

        # API: Submit New RFQ / Inquiry
        if url.path == "/api/inquiries":
            ref_no = f"RFQ-{datetime.now().strftime('%Y')}-{int(datetime.now().timestamp()) % 100000:05d}"
            created_at = datetime.now().isoformat()
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO inquiries (
                reference_no, buyer_name, company_name, email, phone_whatsapp,
                product_name, volume, packaging, destination_port, special_notes,
                status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'new', ?)
            """, (
                ref_no,
                data.get("buyer_name", "Anonymous"),
                data.get("company_name", ""),
                data.get("email", ""),
                data.get("phone_whatsapp", ""),
                data.get("product_name", "Fine Pink Salt"),
                data.get("volume", "20ft FCL"),
                data.get("packaging", "Bulk 25kg"),
                data.get("destination_port", "Karachi Port"),
                data.get("special_notes", ""),
                created_at
            ))
            new_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "id": new_id,
                "reference_no": ref_no,
                "message": "Inquiry recorded in database successfully"
            }).encode("utf-8"))
            return

        # API: Update Inquiry Status
        if url.path == "/api/inquiries/status":
            inquiry_id = data.get("id")
            new_status = data.get("status", "in_review")
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("UPDATE inquiries SET status = ? WHERE id = ?", (new_status, inquiry_id))
            conn.commit()
            conn.close()
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

if __name__ == "__main__":
    init_db()
    print(f"==================================================")
    print(f"🧂 Himalayan Pink Salt Database Server running at:")
    print(f"👉 http://127.0.0.1:{PORT}")
    print(f"📁 SQLite Database: {DB_FILE}")
    print(f"==================================================")
    http.server.HTTPServer(("127.0.0.1", PORT), SaltApiHandler).serve_forever()

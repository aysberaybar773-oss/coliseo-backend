import sqlite3
import os

DB_PATH = "coliseo.db"

def inicializar_bd():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabla de Peleas / Disputas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS peleas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        bando_a TEXT NOT NULL,
        bando_b TEXT NOT NULL,
        votos_a INTEGER DEFAULT 0,
        votos_b INTEGER DEFAULT 0
    );
    """)
    
    # Tabla de Comentarios Anónimos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comentarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pelea_id INTEGER NOT NULL,
        contenido TEXT NOT NULL,
        bando_asignado TEXT NOT NULL,
        fecha TEXT NOT NULL,
        FOREIGN KEY (pelea_id) REFERENCES peleas(id)
    );
    """)
    
    # Si la base de datos está vacía, creamos una pelea por defecto para pruebas
    cursor.execute("SELECT COUNT(*) FROM peleas;")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO peleas (titulo, bando_a, bando_b, votos_a, votos_b)
        VALUES ('¿Capitalismo o Comunismo?', 'Capitalismo', 'Comunismo', 0, 0);
        """)
        
    conn.commit()
    conn.close()

def obtener_pelea(pelea_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM peleas WHERE id = ?;", (pelea_id,))
    pelea = cursor.fetchone()
    
    if not pelea:
        conn.close()
        return None
        
    cursor.execute("SELECT * FROM comentarios WHERE pelea_id = ? ORDER BY fecha DESC;", (pelea_id,))
    comentarios = cursor.fetchall()
    conn.close()
    
    return {
        "id": pelea["id"],
        "titulo": pelea["titulo"],
        "bando_a": pelea["bando_a"],
        "bando_b": pelea["bando_b"],
        "votos_a": pelea["votos_a"],
        "votos_b": pelea["votos_b"],
        "comentarios": [dict(c) for c in comentarios]
    }

def registrar_voto(pelea_id, bando):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if bando == 'A':
        cursor.execute("UPDATE peleas SET votos_a = votos_a + 1 WHERE id = ?;", (pelea_id,))
    elif bando == 'B':
        cursor.execute("UPDATE peleas SET votos_b = votos_b + 1 WHERE id = ?;", (pelea_id,))
    conn.commit()
    conn.close()

def agregar_comentario(pelea_id, contenido, bando):
    from datetime import datetime
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO comentarios (pelea_id, contenido, bando_asignado, fecha)
    VALUES (?, ?, ?, ?);
    """, (pelea_id, contenido, bando, fecha_str))
    conn.commit()
    conn.close()

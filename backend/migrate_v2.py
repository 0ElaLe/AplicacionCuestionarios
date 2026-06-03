"""
migrate_v2.py — Migración aditiva para la versión 2 del sistema.
Ejecutar una sola vez. Es idempotente (usa IF NOT EXISTS / OR IGNORE).
"""
import sqlite3
import uuid

DB_NAME = "database.db"
conn = sqlite3.connect(DB_NAME)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("PRAGMA foreign_keys = OFF")

print("Migrando base de datos a v2...")

# 1. Columnas nuevas en usuarios
try:
    cur.execute("ALTER TABLE usuarios ADD COLUMN password_hash TEXT")
    print("  + usuarios.password_hash")
except Exception:
    print("  = usuarios.password_hash (ya existe)")

try:
    cur.execute("ALTER TABLE usuarios ADD COLUMN rol TEXT NOT NULL DEFAULT 'respondente'")
    print("  + usuarios.rol")
except Exception:
    print("  = usuarios.rol (ya existe)")

# 2. Columnas nuevas en formularios
try:
    cur.execute("ALTER TABLE formularios ADD COLUMN id_creador INTEGER REFERENCES usuarios(id_usuario)")
    print("  + formularios.id_creador")
except Exception:
    print("  = formularios.id_creador (ya existe)")

try:
    cur.execute("ALTER TABLE formularios ADD COLUMN codigo_compartir TEXT")
    print("  + formularios.codigo_compartir")
except Exception:
    print("  = formularios.codigo_compartir (ya existe)")

try:
    cur.execute("ALTER TABLE formularios ADD COLUMN visibilidad TEXT DEFAULT 'publico' CHECK(visibilidad IN ('publico', 'privado'))")
    print("  + formularios.visibilidad")
except Exception:
    print("  = formularios.visibilidad (ya existe)")

# 3. Asignar UUID a formularios existentes sin código
cur.execute("SELECT id_formulario FROM formularios WHERE codigo_compartir IS NULL OR codigo_compartir = ''")
rows = cur.fetchall()
for row in rows:
    codigo = uuid.uuid4().hex[:10].upper()
    cur.execute("UPDATE formularios SET codigo_compartir = ? WHERE id_formulario = ?",
                (codigo, row[0]))
    print(f"  -> formulario {row[0]} asignado codigo: {codigo}")

# 4. Tabla nueva: avance_respuestas (UPSERT de respuestas parciales)
cur.execute("""
CREATE TABLE IF NOT EXISTS avance_respuestas (
    id_avance     INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario    INTEGER NOT NULL,
    id_formulario INTEGER NOT NULL,
    id_pregunta   INTEGER NOT NULL,
    respuesta_texto   TEXT,
    respuesta_numero  REAL,
    opciones_json     TEXT,
    fecha_guardado    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (id_usuario, id_formulario, id_pregunta),

    FOREIGN KEY (id_usuario)    REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_formulario) REFERENCES formularios(id_formulario),
    FOREIGN KEY (id_pregunta)   REFERENCES preguntas(id_pregunta)
)
""")
print("  + tabla avance_respuestas")

conn.commit()
cur.execute("PRAGMA foreign_keys = ON")
cur.execute("PRAGMA integrity_check")
print("\nIntegrity check:", cur.fetchone()[0])
conn.close()
print("\nMigracion completada.")

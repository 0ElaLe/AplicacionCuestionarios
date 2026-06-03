import sqlite3
import os

DB_NAME = "database.db"
SCHEMA_FILE = "schema.sql"
MIGRATE_FILE = "migrate_v2.py"

def init_db():
    print("=== Inicializando Base de Datos ===")
    
    # 1. Crear base de datos y esquema base
    if not os.path.exists(SCHEMA_FILE):
        print(f"Error: No se encontró el archivo {SCHEMA_FILE}")
        return

    print("1. Aplicando esquema base (V1)...")
    with sqlite3.connect(DB_NAME) as conn:
        with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
    print("   Esquema base aplicado correctamente.")

    # 2. Ejecutar migración V2
    if os.path.exists(MIGRATE_FILE):
        print("\n2. Aplicando migraciones (V2)...")
        # Ejecutar el script de migración en el mismo entorno
        os.system(f"python {MIGRATE_FILE}")
    else:
        print(f"\nNo se encontró {MIGRATE_FILE}, saltando migraciones.")
        
    print("\n=== Base de datos lista para usar ===")

if __name__ == "__main__":
    init_db()

import sqlite3

conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print('=== TABLAS ===')
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
for r in cur.fetchall():
    print(' -', r[0])

print('\n=== FORMULARIOS ===')
cur.execute('SELECT * FROM formularios')
for r in cur.fetchall():
    print(dict(r))

print('\n=== TIPOS DE PREGUNTA ===')
cur.execute('SELECT * FROM tipos_pregunta')
for r in cur.fetchall():
    print(dict(r))

print('\n=== PREGUNTAS ===')
cur.execute('''
    SELECT p.id_pregunta, tp.nombre as tipo, p.texto, p.orden, p.obligatoria
    FROM preguntas p
    JOIN tipos_pregunta tp ON p.id_tipo_pregunta = tp.id_tipo_pregunta
    ORDER BY p.orden
''')
for r in cur.fetchall():
    print(dict(r))

print('\n=== OPCIONES POR PREGUNTA ===')
cur.execute('''
    SELECT o.id_opcion, p.texto as pregunta, o.texto, o.valor
    FROM opciones_respuesta o
    JOIN preguntas p ON o.id_pregunta = p.id_pregunta
    ORDER BY o.id_pregunta, o.orden
''')
for r in cur.fetchall():
    print(dict(r))

print('\n=== USUARIOS REGISTRADOS ===')
cur.execute('SELECT id_usuario, nombre, correo, fecha_creacion FROM usuarios')
rows = cur.fetchall()
print(f'Total: {len(rows)}')
for r in rows:
    print(dict(r))

print('\n=== INTENTOS ===')
cur.execute('SELECT * FROM intentos_formulario')
rows = cur.fetchall()
print(f'Total intentos: {len(rows)}')
for r in rows:
    print(dict(r))

print('\n=== CONTEO RESPUESTAS ===')
cur.execute('SELECT COUNT(*) FROM respuestas')
print('Respuestas guardadas:', cur.fetchone()[0])

cur.execute('SELECT COUNT(*) FROM respuestas_opciones')
print('Opciones seleccionadas:', cur.fetchone()[0])

# Integridad referencial basica
print('\n=== INTEGRIDAD ===')
cur.execute('PRAGMA integrity_check')
result = cur.fetchone()[0]
print('integrity_check:', result)

cur.execute('PRAGMA foreign_key_check')
fk_errors = cur.fetchall()
print('foreign_key_check errors:', len(fk_errors) if fk_errors else 0)

conn.close()
print('\n✓ Verificacion completada')

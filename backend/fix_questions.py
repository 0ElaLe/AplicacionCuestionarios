import sqlite3

conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Eliminar definitivamente preguntas 1 y 2 (nombre/correo, ya estan en el login)
cur.execute('DELETE FROM opciones_respuesta WHERE id_pregunta IN (1, 2)')
cur.execute('DELETE FROM respuestas WHERE id_pregunta IN (1, 2)')
cur.execute('DELETE FROM preguntas WHERE id_pregunta IN (1, 2)')

# Asegurar que el orden no tenga duplicados (actualmente hay dos con orden=1 y dos con orden=2)
# Reasignar orden limpio segun id
cur.execute('SELECT id_pregunta FROM preguntas ORDER BY orden, id_pregunta')
ids = [r[0] for r in cur.fetchall()]
for i, pid in enumerate(ids, start=1):
    cur.execute('UPDATE preguntas SET orden = ? WHERE id_pregunta = ?', (i, pid))

conn.commit()

# Verificar resultado final
print('=== PREGUNTAS FINALES ===')
cur.execute('''
    SELECT p.id_pregunta, tp.nombre as tipo, p.texto, p.orden, p.obligatoria
    FROM preguntas p
    JOIN tipos_pregunta tp ON p.id_tipo_pregunta = tp.id_tipo_pregunta
    ORDER BY p.orden
''')
for r in cur.fetchall():
    d = dict(r)
    obligatoria = 'SI' if d['obligatoria'] else 'no'
    print(f"  [{d['orden']}] ({d['tipo']}) {d['texto'][:60]}  [oblig: {obligatoria}]")

print(f'\nTotal preguntas: {len(ids)}')

# Verificar integridad
cur.execute('PRAGMA integrity_check')
print('\nIntegrity check:', cur.fetchone()[0])

conn.close()
print('Verificacion completada.')

import sqlite3

conn = sqlite3.connect('database.db')
cur = conn.cursor()

# Limpiar respuestas existentes para no violar constraints
cur.execute('DELETE FROM respuestas_opciones')
cur.execute('DELETE FROM respuestas')
cur.execute('DELETE FROM intentos_formulario')

# Eliminar preguntas redundantes (nombre y correo, ya se piden en el login)
cur.execute('DELETE FROM preguntas WHERE id_pregunta IN (1, 2)')

# Reordenar preguntas existentes
cur.execute('UPDATE preguntas SET orden = 1 WHERE id_pregunta = 3')
cur.execute('UPDATE preguntas SET orden = 2 WHERE id_pregunta = 4')
cur.execute('UPDATE preguntas SET orden = 3 WHERE id_pregunta = 5')
cur.execute('UPDATE preguntas SET orden = 4 WHERE id_pregunta = 6')

# Mejorar redaccion de preguntas existentes
cur.execute('UPDATE preguntas SET texto = ? WHERE id_pregunta = 3',
    ('¿Te gustó la experiencia con la aplicación?',))
cur.execute('UPDATE preguntas SET texto = ? WHERE id_pregunta = 4',
    ('¿Qué aspectos te parecieron más útiles?',))
cur.execute('UPDATE preguntas SET texto = ? WHERE id_pregunta = 5',
    ('Del 1 al 5, ¿qué calificación general le darías al sistema?',))
cur.execute('UPDATE preguntas SET texto = ? WHERE id_pregunta = 6',
    ('¿Tienes sugerencias o comentarios adicionales para el equipo?',))

# Nueva pregunta 5: frecuencia de uso (opcion_unica = tipo 3)
cur.execute(
    'INSERT INTO preguntas (id_formulario, id_tipo_pregunta, texto, orden, obligatoria) VALUES (?,?,?,?,?)',
    (1, 3, '¿Con qué frecuencia utilizarías este sistema de cuestionarios?', 5, 1)
)
id_frec = cur.lastrowid

# Nueva pregunta 6: dispositivos (opcion_multiple = tipo 4)
cur.execute(
    'INSERT INTO preguntas (id_formulario, id_tipo_pregunta, texto, orden, obligatoria) VALUES (?,?,?,?,?)',
    (1, 4, '¿Desde qué dispositivos accederías a esta plataforma?', 6, 0)
)
id_disp = cur.lastrowid

# Nueva pregunta 7: facilidad de navegacion (escala = tipo 5)
cur.execute(
    'INSERT INTO preguntas (id_formulario, id_tipo_pregunta, texto, orden, obligatoria) VALUES (?,?,?,?,?)',
    (1, 5, '¿Qué tan fácil fue navegar por la plataforma? (1 = muy difícil, 5 = muy fácil)', 7, 1)
)
id_nav = cur.lastrowid

# Nueva pregunta 8: institución (texto_corto = tipo 1)
cur.execute(
    'INSERT INTO preguntas (id_formulario, id_tipo_pregunta, texto, orden, obligatoria) VALUES (?,?,?,?,?)',
    (1, 1, '¿A qué institución o facultad perteneces?', 8, 0)
)

# Opciones: frecuencia
opciones_frec = [
    (id_frec, 'Diariamente', 'diariamente', 1),
    (id_frec, 'Varias veces a la semana', 'varias_semana', 2),
    (id_frec, 'Una vez a la semana', 'una_semana', 3),
    (id_frec, 'Ocasionalmente', 'ocasionalmente', 4),
    (id_frec, 'Solo cuando sea necesario', 'cuando_necesario', 5),
]
cur.executemany(
    'INSERT INTO opciones_respuesta (id_pregunta, texto, valor, orden) VALUES (?,?,?,?)',
    opciones_frec
)

# Opciones: dispositivos
opciones_disp = [
    (id_disp, 'Computadora de escritorio', 'escritorio', 1),
    (id_disp, 'Laptop', 'laptop', 2),
    (id_disp, 'Teléfono celular', 'celular', 3),
    (id_disp, 'Tableta', 'tableta', 4),
]
cur.executemany(
    'INSERT INTO opciones_respuesta (id_pregunta, texto, valor, orden) VALUES (?,?,?,?)',
    opciones_disp
)

# Opciones: escala navegacion (1-5)
opciones_nav = [
    (id_nav, '1', '1', 1),
    (id_nav, '2', '2', 2),
    (id_nav, '3', '3', 3),
    (id_nav, '4', '4', 4),
    (id_nav, '5', '5', 5),
]
cur.executemany(
    'INSERT INTO opciones_respuesta (id_pregunta, texto, valor, orden) VALUES (?,?,?,?)',
    opciones_nav
)

conn.commit()

# Verificar resultado final
print('=== PREGUNTAS FINALES ===')
cur.execute('SELECT id_pregunta, id_tipo_pregunta, texto, orden, obligatoria FROM preguntas ORDER BY orden')
for r in cur.fetchall():
    print(r)

print('\n=== OPCIONES FINALES ===')
cur.execute('SELECT id_opcion, id_pregunta, texto, valor FROM opciones_respuesta ORDER BY id_pregunta, orden')
for r in cur.fetchall():
    print(r)

conn.close()
print('\nOK - Base de datos actualizada correctamente')

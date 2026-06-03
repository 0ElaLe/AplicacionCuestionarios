"""
seed_cuestionario_prueba.py
Crea un cuestionario de prueba sobre satisfacción con la página.
"""
import sqlite3, uuid

DB = "database.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("PRAGMA foreign_keys = ON")

# Código compartido legible
CODIGO = "SECRETO2026"

# Borrar si ya existe para poder re-ejecutar
cur.execute("SELECT id_formulario FROM formularios WHERE codigo_compartir = ?", (CODIGO,))
existing = cur.fetchone()
if existing:
    fid = existing["id_formulario"]
    cur.execute("DELETE FROM respuestas_opciones WHERE id_respuesta IN (SELECT id_respuesta FROM respuestas WHERE id_intento IN (SELECT id_intento FROM intentos_formulario WHERE id_formulario = ?))", (fid,))
    cur.execute("DELETE FROM respuestas WHERE id_intento IN (SELECT id_intento FROM intentos_formulario WHERE id_formulario = ?)", (fid,))
    cur.execute("DELETE FROM intentos_formulario WHERE id_formulario = ?", (fid,))
    cur.execute("DELETE FROM avance_respuestas WHERE id_formulario = ?", (fid,))
    cur.execute("DELETE FROM opciones_respuesta WHERE id_pregunta IN (SELECT id_pregunta FROM preguntas WHERE id_formulario = ?)", (fid,))
    cur.execute("DELETE FROM preguntas WHERE id_formulario = ?", (fid,))
    cur.execute("DELETE FROM formularios WHERE id_formulario = ?", (fid,))
    print(f"Cuestionario anterior ({CODIGO}) eliminado.")

# Crear formulario
cur.execute(
    "INSERT INTO formularios (titulo, descripcion, estado, codigo_compartir, visibilidad) VALUES (?, ?, 'publicado', ?, 'privado')",
    (
        "Cuestionario VIP Privado",
        "Este es un cuestionario de prueba privado. Solo aquellos con la clave SECRETO2026 pueden verlo. ¡No aparece en la pestaña explorar!",
        CODIGO
    )
)
fid = cur.lastrowid

# Preguntas con sus opciones
preguntas = [
    {
        "tipo": "opcion_unica",
        "texto": "¿Cómo calificarías tu experiencia general con esta plataforma?",
        "obligatoria": True,
        "opciones": [
            ("Excelente", "excelente"),
            ("Buena", "buena"),
            ("Regular", "regular"),
            ("Mala", "mala"),
            ("Muy mala", "muy_mala"),
        ]
    },
    {
        "tipo": "escala",
        "texto": "Del 1 al 5, ¿qué calificación le darías al diseño visual de la página?",
        "obligatoria": True,
        "opciones": [("1","1"),("2","2"),("3","3"),("4","4"),("5","5")]
    },
    {
        "tipo": "opcion_unica",
        "texto": "¿Recomendarías esta plataforma a otras personas?",
        "obligatoria": True,
        "opciones": [
            ("Definitivamente sí", "definitivamente_si"),
            ("Probablemente sí", "probablemente_si"),
            ("No estoy seguro/a", "no_seguro"),
            ("Probablemente no", "probablemente_no"),
            ("Definitivamente no", "definitivamente_no"),
        ]
    },
    {
        "tipo": "opcion_multiple",
        "texto": "¿Qué aspectos de la plataforma te parecieron más útiles? (puedes elegir varios)",
        "obligatoria": False,
        "opciones": [
            ("Facilidad para contestar cuestionarios", "facilidad_contestar"),
            ("Diseño limpio e intuitivo", "diseno"),
            ("Rapidez de carga", "rapidez"),
            ("Guardado automático del avance", "guardado_auto"),
            ("Proceso de registro sencillo", "registro"),
            ("Código para compartir fácilmente", "codigo_compartir"),
        ]
    },
    {
        "tipo": "opcion_unica",
        "texto": "¿Encontraste algún problema al usar la plataforma?",
        "obligatoria": True,
        "opciones": [
            ("No, todo funcionó perfecto", "sin_problemas"),
            ("Hubo algún detalle menor", "detalle_menor"),
            ("Sí, tuve varios problemas", "varios_problemas"),
        ]
    },
    {
        "tipo": "escala",
        "texto": "¿Qué tan fácil fue navegar entre las secciones? (1 = muy difícil, 5 = muy fácil)",
        "obligatoria": True,
        "opciones": [("1","1"),("2","2"),("3","3"),("4","4"),("5","5")]
    },
    {
        "tipo": "opcion_unica",
        "texto": "¿Desde qué tipo de dispositivo usaste la plataforma?",
        "obligatoria": True,
        "opciones": [
            ("Computadora de escritorio", "escritorio"),
            ("Laptop", "laptop"),
            ("Teléfono celular", "celular"),
            ("Tableta", "tableta"),
        ]
    },
    {
        "tipo": "texto_largo",
        "texto": "¿Tienes alguna sugerencia concreta para mejorar la plataforma?",
        "obligatoria": False,
        "opciones": []
    },
    {
        "tipo": "texto_corto",
        "texto": "¿Cuál es tu ocupación o área de estudio? (opcional)",
        "obligatoria": False,
        "opciones": []
    },
]

for orden, p in enumerate(preguntas, start=1):
    cur.execute(
        "SELECT id_tipo_pregunta FROM tipos_pregunta WHERE nombre = ?",
        (p["tipo"],)
    )
    tipo_id = cur.fetchone()["id_tipo_pregunta"]

    cur.execute(
        "INSERT INTO preguntas (id_formulario, id_tipo_pregunta, texto, orden, obligatoria) VALUES (?,?,?,?,?)",
        (fid, tipo_id, p["texto"], orden, 1 if p["obligatoria"] else 0)
    )
    pid = cur.lastrowid

    for i, (texto, valor) in enumerate(p["opciones"], start=1):
        cur.execute(
            "INSERT INTO opciones_respuesta (id_pregunta, texto, valor, orden) VALUES (?,?,?,?)",
            (pid, texto, valor, i)
        )

conn.commit()
conn.close()

print(f"\nCuestionario creado exitosamente.")
print(f"  Titulo  : Evaluacion del Sistema de Cuestionarios")
print(f"  ID      : {fid}")
print(f"  Codigo  : {CODIGO}")
print(f"  URL     : http://localhost:5173/contestar/{CODIGO}")
print(f"  Preguntas: {len(preguntas)}")

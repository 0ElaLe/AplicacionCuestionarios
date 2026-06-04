import sqlite3
import uuid
import hashlib
import json

DB_NAME = "database.db"



def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def inicializar_bd():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        correo TEXT NOT NULL UNIQUE,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS formularios (
        id_formulario INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        descripcion TEXT,
        estado TEXT NOT NULL DEFAULT 'publicado',
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS tipos_pregunta (
        id_tipo_pregunta INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        descripcion TEXT
    );

    CREATE TABLE IF NOT EXISTS preguntas (
        id_pregunta INTEGER PRIMARY KEY AUTOINCREMENT,
        id_formulario INTEGER NOT NULL,
        id_tipo_pregunta INTEGER NOT NULL,
        texto TEXT NOT NULL,
        orden INTEGER NOT NULL,
        obligatoria INTEGER NOT NULL DEFAULT 1,

        FOREIGN KEY (id_formulario)
            REFERENCES formularios(id_formulario),

        FOREIGN KEY (id_tipo_pregunta)
            REFERENCES tipos_pregunta(id_tipo_pregunta)
    );

    CREATE TABLE IF NOT EXISTS opciones_respuesta (
        id_opcion INTEGER PRIMARY KEY AUTOINCREMENT,
        id_pregunta INTEGER NOT NULL,
        texto TEXT NOT NULL,
        valor TEXT,
        orden INTEGER NOT NULL,

        FOREIGN KEY (id_pregunta)
            REFERENCES preguntas(id_pregunta)
    );

    CREATE TABLE IF NOT EXISTS intentos_formulario (
        id_intento INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario INTEGER NOT NULL,
        id_formulario INTEGER NOT NULL,
        estado TEXT NOT NULL DEFAULT 'enviado',
        fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (id_usuario)
            REFERENCES usuarios(id_usuario),

        FOREIGN KEY (id_formulario)
            REFERENCES formularios(id_formulario),

        UNIQUE (id_usuario, id_formulario)
    );

    CREATE TABLE IF NOT EXISTS respuestas (
        id_respuesta INTEGER PRIMARY KEY AUTOINCREMENT,
        id_intento INTEGER NOT NULL,
        id_pregunta INTEGER NOT NULL,
        respuesta_texto TEXT,
        respuesta_numero REAL,
        respuesta_fecha TEXT,
        fecha_respuesta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (id_intento)
            REFERENCES intentos_formulario(id_intento),

        FOREIGN KEY (id_pregunta)
            REFERENCES preguntas(id_pregunta),

        UNIQUE (id_intento, id_pregunta)
    );

    CREATE TABLE IF NOT EXISTS respuestas_opciones (
        id_respuesta INTEGER NOT NULL,
        id_opcion INTEGER NOT NULL,

        PRIMARY KEY (id_respuesta, id_opcion),

        FOREIGN KEY (id_respuesta)
            REFERENCES respuestas(id_respuesta),

        FOREIGN KEY (id_opcion)
            REFERENCES opciones_respuesta(id_opcion)
    );
    """)

    insertar_datos_semilla(cursor)

    conn.commit()
    conn.close()


def insertar_datos_semilla(cursor):
    cursor.executescript("""
    INSERT OR IGNORE INTO tipos_pregunta
    (id_tipo_pregunta, nombre, descripcion)
    VALUES
    (1, 'texto_corto', 'Respuesta textual breve'),
    (2, 'texto_largo', 'Respuesta textual extensa'),
    (3, 'opcion_unica', 'Selección de una sola opción'),
    (4, 'opcion_multiple', 'Selección de varias opciones'),
    (5, 'escala', 'Respuesta numérica dentro de una escala'),
    (6, 'si_no', 'Pregunta de Sí o No'),
    (7, 'fecha', 'Respuesta de tipo fecha');

    INSERT OR IGNORE INTO formularios
    (id_formulario, titulo, descripcion, estado)
    VALUES
    (
        1,
        'Encuesta de satisfacción',
        'Formulario de prueba para la primera versión del sistema',
        'publicado'
    );

    INSERT OR IGNORE INTO preguntas
    (id_pregunta, id_formulario, id_tipo_pregunta, texto, orden, obligatoria)
    VALUES
    (1, 1, 1, '¿Cuál es tu nombre?', 1, 1),
    (2, 1, 1, '¿Cuál es tu correo electrónico?', 2, 1),
    (3, 1, 3, '¿Te gustó la aplicación?', 3, 1),
    (4, 1, 4, '¿Qué aspectos te parecieron más útiles?', 4, 0),
    (5, 1, 5, 'Del 1 al 5, ¿qué calificación le das a la aplicación?', 5, 1),
    (6, 1, 2, 'Escribe algún comentario adicional.', 6, 0);

    INSERT OR IGNORE INTO opciones_respuesta
    (id_opcion, id_pregunta, texto, valor, orden)
    VALUES
    (1, 3, 'Sí', 'si', 1),
    (2, 3, 'No', 'no', 2),
    (3, 4, 'Diseño visual', 'diseno_visual', 1),
    (4, 4, 'Facilidad de uso', 'facilidad_uso', 2),
    (5, 4, 'Rapidez', 'rapidez', 3),
    (6, 4, 'Claridad de las preguntas', 'claridad_preguntas', 4),
    (7, 5, '1', '1', 1),
    (8, 5, '2', '2', 2),
    (9, 5, '3', '3', 3),
    (10, 5, '4', '4', 4),
    (11, 5, '5', '5', 5);
    """)


def row_to_dict(row):
    if row is None:
        return None

    return dict(row)


def crear_o_obtener_usuario(nombre, correo):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id_usuario, nombre, correo, fecha_creacion
        FROM usuarios
        WHERE correo = ?
    """, (correo,))

    usuario = cursor.fetchone()

    if usuario:
        # Si el nombre cambió, lo actualizamos
        if usuario["nombre"] != nombre:
            cursor.execute("""
                UPDATE usuarios SET nombre = ? WHERE correo = ?
            """, (nombre, correo))
            conn.commit()

        cursor.execute("""
            SELECT id_usuario, nombre, correo, fecha_creacion
            FROM usuarios WHERE correo = ?
        """, (correo,))
        usuario = cursor.fetchone()
        conn.close()
        return row_to_dict(usuario)

    cursor.execute("""
        INSERT INTO usuarios (nombre, correo)
        VALUES (?, ?)
    """, (nombre, correo))

    conn.commit()

    id_usuario = cursor.lastrowid

    cursor.execute("""
        SELECT id_usuario, nombre, correo, fecha_creacion
        FROM usuarios
        WHERE id_usuario = ?
    """, (id_usuario,))

    usuario = cursor.fetchone()

    conn.close()

    return row_to_dict(usuario)


def obtener_formulario(id_formulario):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id_formulario, titulo, descripcion, estado, visibilidad, codigo_compartir, id_creador, fecha_creacion
        FROM formularios
        WHERE id_formulario = ?
    """, (id_formulario,))

    formulario = cursor.fetchone()

    if formulario is None:
        conn.close()
        return None

    formulario_dict = row_to_dict(formulario)

    cursor.execute("""
        SELECT 
            p.id_pregunta,
            p.texto,
            p.orden,
            p.obligatoria,
            tp.nombre AS tipo
        FROM preguntas p
        INNER JOIN tipos_pregunta tp
            ON p.id_tipo_pregunta = tp.id_tipo_pregunta
        WHERE p.id_formulario = ?
        ORDER BY p.orden
    """, (id_formulario,))

    preguntas = cursor.fetchall()

    preguntas_lista = []

    for pregunta in preguntas:
        pregunta_dict = row_to_dict(pregunta)

        cursor.execute("""
            SELECT id_opcion, texto, valor, orden
            FROM opciones_respuesta
            WHERE id_pregunta = ?
            ORDER BY orden
        """, (pregunta_dict["id_pregunta"],))

        opciones = cursor.fetchall()

        pregunta_dict["opciones"] = [
            row_to_dict(opcion)
            for opcion in opciones
        ]

        preguntas_lista.append(pregunta_dict)

    formulario_dict["preguntas"] = preguntas_lista

    conn.close()

    return formulario_dict


def usuario_respondio_formulario(id_usuario, id_formulario):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id_intento
        FROM intentos_formulario
        WHERE id_usuario = ?
          AND id_formulario = ?
          AND estado = 'enviado'
    """, (id_usuario, id_formulario))

    intento = cursor.fetchone()

    conn.close()

    return intento is not None


def eliminar_intento_usuario(id_usuario, id_formulario):
    """Elimina el intento previo y todas sus respuestas para permitir reintentar."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN")

        # Obtener el id del intento
        cursor.execute("""
            SELECT id_intento FROM intentos_formulario
            WHERE id_usuario = ? AND id_formulario = ?
        """, (id_usuario, id_formulario))

        intento = cursor.fetchone()
        if intento is None:
            conn.rollback()
            conn.close()
            return False

        id_intento = intento["id_intento"]

        # Eliminar opciones seleccionadas
        cursor.execute("""
            DELETE FROM respuestas_opciones
            WHERE id_respuesta IN (
                SELECT id_respuesta FROM respuestas WHERE id_intento = ?
            )
        """, (id_intento,))

        # Eliminar respuestas
        cursor.execute("""
            DELETE FROM respuestas WHERE id_intento = ?
        """, (id_intento,))

        # Eliminar el intento
        cursor.execute("""
            DELETE FROM intentos_formulario WHERE id_intento = ?
        """, (id_intento,))

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()



def obtener_tipo_pregunta(cursor, id_pregunta, id_formulario):
    cursor.execute("""
        SELECT 
            p.id_pregunta,
            p.obligatoria,
            tp.nombre AS tipo
        FROM preguntas p
        INNER JOIN tipos_pregunta tp
            ON p.id_tipo_pregunta = tp.id_tipo_pregunta
        WHERE p.id_pregunta = ?
          AND p.id_formulario = ?
    """, (id_pregunta, id_formulario))

    return cursor.fetchone()


def opcion_pertenece_a_pregunta(cursor, id_opcion, id_pregunta):
    cursor.execute("""
        SELECT id_opcion
        FROM opciones_respuesta
        WHERE id_opcion = ?
          AND id_pregunta = ?
    """, (id_opcion, id_pregunta))

    return cursor.fetchone() is not None


def guardar_respuestas(id_usuario, id_formulario, respuestas):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN")

        # UPSERT: si ya existe un intento en_progreso lo sobreescribe con 'enviado'
        cursor.execute("""
            INSERT INTO intentos_formulario (id_usuario, id_formulario, estado)
            VALUES (?, ?, 'enviado')
            ON CONFLICT(id_usuario, id_formulario)
            DO UPDATE SET estado = 'enviado'
        """, (id_usuario, id_formulario))

        # Obtener el id_intento (recién insertado o el que ya existía)
        cursor.execute(
            "SELECT id_intento FROM intentos_formulario WHERE id_usuario = ? AND id_formulario = ?",
            (id_usuario, id_formulario)
        )
        id_intento = cursor.fetchone()["id_intento"]

        for respuesta in respuestas:
            id_pregunta = respuesta.get("id_pregunta")

            if not id_pregunta:
                raise ValueError("Todas las respuestas deben incluir id_pregunta")

            pregunta = obtener_tipo_pregunta(
                cursor,
                id_pregunta,
                id_formulario
            )

            if pregunta is None:
                raise ValueError(
                    f"La pregunta {id_pregunta} no pertenece al formulario"
                )

            tipo = pregunta["tipo"]

            respuesta_texto = None
            respuesta_numero = None
            respuesta_fecha = None

            if tipo in ["texto_corto", "texto_largo"]:
                respuesta_texto = respuesta.get("respuesta_texto")

                if pregunta["obligatoria"] and not respuesta_texto:
                    raise ValueError(
                        f"La pregunta {id_pregunta} es obligatoria"
                    )

            elif tipo == "escala":
                respuesta_numero = respuesta.get("respuesta_numero")

                if pregunta["obligatoria"] and respuesta_numero is None:
                    raise ValueError(
                        f"La pregunta {id_pregunta} es obligatoria"
                    )

                if respuesta_numero is not None:
                    respuesta_numero = float(respuesta_numero)

                    if respuesta_numero < 1 or respuesta_numero > 5:
                        raise ValueError(
                            "La escala debe estar entre 1 y 5"
                        )

            elif tipo in ["opcion_unica", "opcion_multiple", "si_no"]:
                opciones = respuesta.get("opciones", [])

                if pregunta["obligatoria"] and len(opciones) == 0:
                    raise ValueError(
                        f"La pregunta {id_pregunta} es obligatoria"
                    )

                if tipo in ["opcion_unica", "si_no"] and len(opciones) > 1:
                    raise ValueError(
                        f"La pregunta {id_pregunta} solo permite una opción"
                    )

                for id_opcion in opciones:
                    if not opcion_pertenece_a_pregunta(
                        cursor,
                        id_opcion,
                        id_pregunta
                    ):
                        raise ValueError(
                            f"La opción {id_opcion} no pertenece a la pregunta {id_pregunta}"
                        )

            elif tipo == "fecha":
                respuesta_texto = respuesta.get("respuesta_texto")
                if pregunta["obligatoria"] and not respuesta_texto:
                    raise ValueError(
                        f"La pregunta {id_pregunta} es obligatoria"
                    )

            else:
                raise ValueError(
                    f"Tipo de pregunta no soportado: {tipo}"
                )

            cursor.execute("""
                INSERT INTO respuestas
                (
                    id_intento,
                    id_pregunta,
                    respuesta_texto,
                    respuesta_numero,
                    respuesta_fecha
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                id_intento,
                id_pregunta,
                respuesta_texto,
                respuesta_numero,
                respuesta_fecha
            ))

            id_respuesta = cursor.lastrowid

            if tipo in ["opcion_unica", "opcion_multiple", "si_no"]:
                opciones = respuesta.get("opciones", [])

                for id_opcion in opciones:
                    cursor.execute("""
                        INSERT INTO respuestas_opciones
                        (id_respuesta, id_opcion)
                        VALUES (?, ?)
                    """, (id_respuesta, id_opcion))

        conn.commit()

        # Limpiar avance temporal ahora que ya está guardado definitivamente
        try:
            cursor.execute(
                "DELETE FROM avance_respuestas WHERE id_usuario = ? AND id_formulario = ?",
                (id_usuario, id_formulario)
            )
            conn.commit()
        except Exception:
            pass  # No crítico si falla

        return {
            "id_intento": id_intento
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def obtener_respuestas_usuario(id_usuario, id_formulario):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id_intento
        FROM intentos_formulario
        WHERE id_usuario = ?
          AND id_formulario = ?
          AND estado = 'enviado'
    """, (id_usuario, id_formulario))

    intento = cursor.fetchone()

    if intento is None:
        conn.close()
        return None

    id_intento = intento["id_intento"]

    cursor.execute("""
        SELECT
            r.id_respuesta,
            r.id_pregunta,
            p.texto AS pregunta,
            tp.nombre AS tipo,
            r.respuesta_texto,
            r.respuesta_numero,
            r.respuesta_fecha
        FROM respuestas r
        INNER JOIN preguntas p
            ON r.id_pregunta = p.id_pregunta
        INNER JOIN tipos_pregunta tp
            ON p.id_tipo_pregunta = tp.id_tipo_pregunta
        WHERE r.id_intento = ?
        ORDER BY p.orden
    """, (id_intento,))

    respuestas = cursor.fetchall()

    resultado = []

    for respuesta in respuestas:
        respuesta_dict = row_to_dict(respuesta)

        cursor.execute("""
            SELECT
                op.id_opcion,
                op.texto,
                op.valor
            FROM respuestas_opciones ro
            INNER JOIN opciones_respuesta op
                ON ro.id_opcion = op.id_opcion
            WHERE ro.id_respuesta = ?
            ORDER BY op.orden
        """, (respuesta_dict["id_respuesta"],))

        opciones = cursor.fetchall()

        respuesta_dict["opciones_seleccionadas"] = [
            row_to_dict(opcion)
            for opcion in opciones
        ]

        resultado.append(respuesta_dict)

    conn.close()

    return resultado


# ═══════════════════════════════════════════════════════════════
#  V2 — AUTENTICACION
# ═══════════════════════════════════════════════════════════════

def _hash_password(password: str) -> str:
    """Hashea la contraseña con SHA-256 + salt fijo. Simple y sin dependencias."""
    salt = "iimas-unam-2026"
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


def registrar_usuario(nombre: str, correo: str, password: str):
    """Crea un nuevo usuario con contraseña hasheada. Error si el correo ya existe."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id_usuario FROM usuarios WHERE correo = ?", (correo,))
    if cursor.fetchone():
        conn.close()
        raise ValueError("El correo ya esta registrado")

    ph = _hash_password(password)
    cursor.execute(
        "INSERT INTO usuarios (nombre, correo, password_hash, rol) VALUES (?, ?, ?, 'respondente')",
        (nombre, correo, ph)
    )
    conn.commit()
    uid = cursor.lastrowid
    cursor.execute(
        "SELECT id_usuario, nombre, correo, rol, fecha_creacion FROM usuarios WHERE id_usuario = ?",
        (uid,)
    )
    user = row_to_dict(cursor.fetchone())
    conn.close()
    return user


def login_usuario(correo: str, password: str):
    """Valida credenciales. Retorna el usuario o None si son incorrectas."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id_usuario, nombre, correo, rol, password_hash, fecha_creacion FROM usuarios WHERE correo = ?",
        (correo,)
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    ph = _hash_password(password)
    if row["password_hash"] != ph:
        return None

    d = dict(row)
    d.pop("password_hash", None)
    return d


# ═══════════════════════════════════════════════════════════════
#  V2 — FORMULARIOS DINAMICOS
# ═══════════════════════════════════════════════════════════════

def crear_formulario_v2(id_creador: int, titulo: str, descripcion: str, preguntas_data: list, visibilidad: str = "publico"):
    """
    Crea un formulario completo con sus preguntas y opciones.
    preguntas_data: lista de {tipo, texto, obligatoria, opciones: [{texto, valor}]}
    Retorna el formulario creado con su codigo_compartir.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN")
        codigo = uuid.uuid4().hex[:10].upper()

        cursor.execute(
            "INSERT INTO formularios (titulo, descripcion, estado, id_creador, codigo_compartir, visibilidad) VALUES (?, ?, 'publicado', ?, ?, ?)",
            (titulo, descripcion, id_creador, codigo, visibilidad)
        )
        id_formulario = cursor.lastrowid


        for orden, p in enumerate(preguntas_data, start=1):
            cursor.execute(
                "SELECT id_tipo_pregunta FROM tipos_pregunta WHERE nombre = ?",
                (p["tipo"],)
            )
            tipo_row = cursor.fetchone()
            if not tipo_row:
                raise ValueError(f"Tipo de pregunta desconocido: {p['tipo']}")

            cursor.execute(
                "INSERT INTO preguntas (id_formulario, id_tipo_pregunta, texto, orden, obligatoria) VALUES (?, ?, ?, ?, ?)",
                (id_formulario, tipo_row["id_tipo_pregunta"], p["texto"], orden, 1 if p.get("obligatoria", True) else 0)
            )
            id_pregunta = cursor.lastrowid

            if p["tipo"] == "si_no":
                cursor.execute(
                    "INSERT INTO opciones_respuesta (id_pregunta, texto, valor, orden) VALUES (?, 'Sí', 'si', 1)",
                    (id_pregunta,)
                )
                cursor.execute(
                    "INSERT INTO opciones_respuesta (id_pregunta, texto, valor, orden) VALUES (?, 'No', 'no', 2)",
                    (id_pregunta,)
                )
            else:
                for i, opt in enumerate(p.get("opciones", []), start=1):
                    cursor.execute(
                        "INSERT INTO opciones_respuesta (id_pregunta, texto, valor, orden) VALUES (?, ?, ?, ?)",
                        (id_pregunta, opt["texto"], opt.get("valor", opt["texto"].lower().replace(" ", "_")), i)
                    )

        conn.commit()
        conn.close()
        return {"id_formulario": id_formulario, "codigo_compartir": codigo}

    except Exception:
        conn.rollback()
        conn.close()
        raise


def obtener_formulario_por_codigo(codigo: str):
    """Busca un formulario publicado por su codigo_compartir."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id_formulario FROM formularios WHERE codigo_compartir = ? AND estado = 'publicado'",
        (codigo.upper(),)
    )
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return obtener_formulario(row["id_formulario"])


def obtener_formularios_de_usuario(id_usuario: int):
    """Lista todos los formularios creados por el usuario."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id_formulario, titulo, descripcion, estado, codigo_compartir, fecha_creacion FROM formularios WHERE id_creador = ? ORDER BY fecha_creacion DESC",
        (id_usuario,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


# ═══════════════════════════════════════════════════════════════
#  V2 — GUARDADO DE AVANCE
# ═══════════════════════════════════════════════════════════════

def guardar_avance(id_usuario: int, id_formulario: int, respuestas_parciales: list):
    """
    Guarda o actualiza respuestas parciales (en_progreso).
    No lanza error si el usuario ya envió definitivamente — solo ignora.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Verificar si ya está enviado
    cursor.execute(
        "SELECT estado FROM intentos_formulario WHERE id_usuario = ? AND id_formulario = ?",
        (id_usuario, id_formulario)
    )
    intento = cursor.fetchone()
    if intento and intento["estado"] == "enviado":
        conn.close()
        return False  # Ya enviado, no se puede modificar

    # Crear intento en_progreso si no existe
    if not intento:
        cursor.execute(
            "INSERT OR IGNORE INTO intentos_formulario (id_usuario, id_formulario, estado) VALUES (?, ?, 'en_progreso')",
            (id_usuario, id_formulario)
        )
    else:
        cursor.execute(
            "UPDATE intentos_formulario SET estado = 'en_progreso' WHERE id_usuario = ? AND id_formulario = ?",
            (id_usuario, id_formulario)
        )

    for r in respuestas_parciales:
        id_pregunta = r.get("id_pregunta")
        if not id_pregunta:
            continue
        opciones_json = json.dumps(r.get("opciones", [])) if r.get("opciones") is not None else None
        cursor.execute(
            """INSERT INTO avance_respuestas (id_usuario, id_formulario, id_pregunta, respuesta_texto, respuesta_numero, opciones_json)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(id_usuario, id_formulario, id_pregunta)
               DO UPDATE SET respuesta_texto=excluded.respuesta_texto,
                             respuesta_numero=excluded.respuesta_numero,
                             opciones_json=excluded.opciones_json,
                             fecha_guardado=CURRENT_TIMESTAMP""",
            (id_usuario, id_formulario, id_pregunta,
             r.get("respuesta_texto"), r.get("respuesta_numero"), opciones_json)
        )

    conn.commit()
    conn.close()
    return True


def obtener_avance(id_usuario: int, id_formulario: int):
    """Recupera el avance guardado de un usuario en un formulario."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT estado FROM intentos_formulario WHERE id_usuario = ? AND id_formulario = ?",
        (id_usuario, id_formulario)
    )
    intento = cursor.fetchone()
    estado = intento["estado"] if intento else None

    cursor.execute(
        "SELECT id_pregunta, respuesta_texto, respuesta_numero, opciones_json FROM avance_respuestas WHERE id_usuario = ? AND id_formulario = ?",
        (id_usuario, id_formulario)
    )
    rows = cursor.fetchall()
    conn.close()

    respuestas = []
    for r in rows:
        d = dict(r)
        if d["opciones_json"]:
            d["opciones"] = json.loads(d["opciones_json"])
        else:
            d["opciones"] = []
        del d["opciones_json"]
        respuestas.append(d)

    return {"estado": estado, "respuestas": respuestas}


# ═══════════════════════════════════════════════════════════════
#  V2 — EXPLORACION DE FORMULARIOS
# ═══════════════════════════════════════════════════════════════

def obtener_formularios_publicos():
    """Todos los formularios publicados con conteo de preguntas y respondentes."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            f.id_formulario,
            f.titulo,
            f.descripcion,
            f.codigo_compartir,
            f.fecha_creacion,
            f.visibilidad,
            u.nombre AS creado_por,
            COUNT(DISTINCT p.id_pregunta)  AS total_preguntas,
            COUNT(DISTINCT i.id_intento)   AS total_respuestas
        FROM formularios f
        LEFT JOIN usuarios   u ON f.id_creador    = u.id_usuario
        LEFT JOIN preguntas  p ON p.id_formulario = f.id_formulario
        LEFT JOIN intentos_formulario i
               ON i.id_formulario = f.id_formulario AND i.estado = 'enviado'
        WHERE f.estado = 'publicado' AND f.visibilidad = 'publico'
        GROUP BY f.id_formulario
        ORDER BY f.fecha_creacion DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


def obtener_formulario_por_id(id_formulario: int, id_usuario: int):
    """Devuelve el formulario completo solo si el usuario es su creador."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id_creador FROM formularios WHERE id_formulario = ?",
        (id_formulario,)
    )
    row = cursor.fetchone()
    conn.close()
    if row is None or row["id_creador"] != id_usuario:
        return None
    return obtener_formulario(id_formulario)


def _contar_respuestas(id_formulario: int, cursor) -> int:
    cursor.execute(
        "SELECT COUNT(*) AS total FROM intentos_formulario WHERE id_formulario = ? AND estado = 'enviado'",
        (id_formulario,)
    )
    return cursor.fetchone()["total"]


def editar_formulario_v2(id_formulario: int, id_usuario: int, titulo: str, descripcion: str, visibilidad: str, preguntas_data: list):
    """
    Actualiza un formulario. Siempre actualiza metadatos.
    Actualiza las preguntas solo si no hay respuestas todavía.
    Retorna {'preguntas_editadas': bool, 'tiene_respuestas': bool}.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id_creador FROM formularios WHERE id_formulario = ?",
        (id_formulario,)
    )
    form = cursor.fetchone()
    if form is None or form["id_creador"] != id_usuario:
        conn.close()
        raise PermissionError("No tienes permiso para editar este cuestionario")

    total = _contar_respuestas(id_formulario, cursor)

    try:
        cursor.execute("BEGIN")

        cursor.execute(
            "UPDATE formularios SET titulo = ?, descripcion = ?, visibilidad = ? WHERE id_formulario = ?",
            (titulo, descripcion, visibilidad, id_formulario)
        )

        preguntas_editadas = False
        if total == 0 and preguntas_data:
            cursor.execute(
                "SELECT id_pregunta FROM preguntas WHERE id_formulario = ?",
                (id_formulario,)
            )
            ids_preguntas = [r["id_pregunta"] for r in cursor.fetchall()]

            if ids_preguntas:
                placeholders = ",".join("?" * len(ids_preguntas))
                cursor.execute(
                    f"DELETE FROM opciones_respuesta WHERE id_pregunta IN ({placeholders})",
                    ids_preguntas
                )
                cursor.execute(
                    f"DELETE FROM preguntas WHERE id_pregunta IN ({placeholders})",
                    ids_preguntas
                )

            for orden, p in enumerate(preguntas_data, start=1):
                cursor.execute(
                    "SELECT id_tipo_pregunta FROM tipos_pregunta WHERE nombre = ?",
                    (p["tipo"],)
                )
                tipo_row = cursor.fetchone()
                if not tipo_row:
                    raise ValueError(f"Tipo de pregunta desconocido: {p['tipo']}")

                cursor.execute(
                    "INSERT INTO preguntas (id_formulario, id_tipo_pregunta, texto, orden, obligatoria) VALUES (?, ?, ?, ?, ?)",
                    (id_formulario, tipo_row["id_tipo_pregunta"], p["texto"], orden,
                     1 if p.get("obligatoria", True) else 0)
                )
                id_pregunta = cursor.lastrowid

                if p["tipo"] == "si_no":
                    cursor.execute(
                        "INSERT INTO opciones_respuesta (id_pregunta, texto, valor, orden) VALUES (?, 'Sí', 'si', 1)",
                        (id_pregunta,)
                    )
                    cursor.execute(
                        "INSERT INTO opciones_respuesta (id_pregunta, texto, valor, orden) VALUES (?, 'No', 'no', 2)",
                        (id_pregunta,)
                    )
                else:
                    for i, opt in enumerate(p.get("opciones", []), start=1):
                        cursor.execute(
                            "INSERT INTO opciones_respuesta (id_pregunta, texto, valor, orden) VALUES (?, ?, ?, ?)",
                            (id_pregunta, opt["texto"],
                             opt.get("valor", opt["texto"].lower().replace(" ", "_")), i)
                        )

            preguntas_editadas = True

        conn.commit()
        return {"preguntas_editadas": preguntas_editadas, "tiene_respuestas": total > 0}

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def archivar_formulario(id_formulario: int, id_usuario: int):
    """Alterna el estado publicado/archivado de un formulario."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id_creador, estado FROM formularios WHERE id_formulario = ?",
        (id_formulario,)
    )
    form = cursor.fetchone()
    if form is None or form["id_creador"] != id_usuario:
        conn.close()
        raise PermissionError("No tienes permiso para archivar este cuestionario")

    nuevo_estado = "archivado" if form["estado"] == "publicado" else "publicado"
    cursor.execute(
        "UPDATE formularios SET estado = ? WHERE id_formulario = ?",
        (nuevo_estado, id_formulario)
    )
    conn.commit()
    conn.close()
    return {"estado": nuevo_estado}


def obtener_resultados_formulario(id_formulario: int, id_usuario: int):
    """
    Devuelve las respuestas agregadas por pregunta para el creador del formulario.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id_formulario, titulo, descripcion, id_creador FROM formularios WHERE id_formulario = ?",
        (id_formulario,)
    )
    form = cursor.fetchone()
    if form is None or form["id_creador"] != id_usuario:
        conn.close()
        return None

    total_respuestas = _contar_respuestas(id_formulario, cursor)

    cursor.execute("""
        SELECT p.id_pregunta, p.texto, p.orden, p.obligatoria, tp.nombre AS tipo
        FROM preguntas p
        INNER JOIN tipos_pregunta tp ON p.id_tipo_pregunta = tp.id_tipo_pregunta
        WHERE p.id_formulario = ?
        ORDER BY p.orden
    """, (id_formulario,))
    preguntas = cursor.fetchall()

    resultado_preguntas = []
    for pregunta in preguntas:
        p = dict(pregunta)
        tipo = p["tipo"]
        id_pregunta = p["id_pregunta"]

        if tipo in ["texto_corto", "texto_largo", "fecha"]:
            cursor.execute("""
                SELECT r.respuesta_texto
                FROM respuestas r
                INNER JOIN intentos_formulario i ON r.id_intento = i.id_intento
                WHERE r.id_pregunta = ? AND i.id_formulario = ? AND i.estado = 'enviado'
                  AND r.respuesta_texto IS NOT NULL AND r.respuesta_texto != ''
            """, (id_pregunta, id_formulario))
            p["respuestas_texto"] = [row["respuesta_texto"] for row in cursor.fetchall()]

        elif tipo == "escala":
            cursor.execute("""
                SELECT r.respuesta_numero
                FROM respuestas r
                INNER JOIN intentos_formulario i ON r.id_intento = i.id_intento
                WHERE r.id_pregunta = ? AND i.id_formulario = ? AND i.estado = 'enviado'
                  AND r.respuesta_numero IS NOT NULL
            """, (id_pregunta, id_formulario))
            numeros = [row["respuesta_numero"] for row in cursor.fetchall()]
            if numeros:
                p["promedio"] = round(sum(numeros) / len(numeros), 1)
                dist = {}
                for n in numeros:
                    key = str(int(n))
                    dist[key] = dist.get(key, 0) + 1
                p["distribucion"] = dist
            else:
                p["promedio"] = None
                p["distribucion"] = {}
            p["total"] = len(numeros)

        elif tipo in ["opcion_unica", "opcion_multiple", "si_no"]:
            cursor.execute("""
                SELECT o.id_opcion, o.texto, COUNT(ro.id_opcion) AS conteo
                FROM opciones_respuesta o
                LEFT JOIN respuestas_opciones ro ON o.id_opcion = ro.id_opcion
                LEFT JOIN respuestas r ON ro.id_respuesta = r.id_respuesta
                LEFT JOIN intentos_formulario i
                       ON r.id_intento = i.id_intento
                      AND i.id_formulario = ? AND i.estado = 'enviado'
                WHERE o.id_pregunta = ?
                GROUP BY o.id_opcion
                ORDER BY o.orden
            """, (id_formulario, id_pregunta))
            opciones = cursor.fetchall()
            total_sel = sum(o["conteo"] for o in opciones)
            p["opciones"] = [
                {
                    "id_opcion": o["id_opcion"],
                    "texto": o["texto"],
                    "conteo": o["conteo"],
                    "porcentaje": round(o["conteo"] / total_sel * 100) if total_sel > 0 else 0
                }
                for o in opciones
            ]

        resultado_preguntas.append(p)

    conn.close()
    return {
        "formulario": dict(form),
        "total_respuestas": total_respuestas,
        "preguntas": resultado_preguntas
    }


def obtener_formularios_respondidos(id_usuario: int):
    """Formularios que el usuario ya respondio (estado = enviado)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            f.id_formulario,
            f.titulo,
            f.descripcion,
            f.codigo_compartir,
            i.fecha_envio AS fecha_intento,
            u.nombre AS creado_por,
            COUNT(DISTINCT p.id_pregunta) AS total_preguntas,
            COUNT(DISTINCT r.id_respuesta) AS preguntas_respondidas
        FROM intentos_formulario i
        INNER JOIN formularios f ON i.id_formulario = f.id_formulario
        LEFT JOIN  usuarios    u ON f.id_creador     = u.id_usuario
        LEFT JOIN  preguntas   p ON p.id_formulario  = f.id_formulario
        LEFT JOIN  respuestas  r ON r.id_intento     = i.id_intento
        WHERE i.id_usuario = ? AND i.estado = 'enviado'
        GROUP BY f.id_formulario
        ORDER BY i.fecha_envio DESC
    """, (id_usuario,))
    rows = cursor.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]

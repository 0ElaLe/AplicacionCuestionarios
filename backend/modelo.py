import sqlite3

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
    (5, 'escala', 'Respuesta numérica dentro de una escala');

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
        SELECT id_formulario, titulo, descripcion, estado, fecha_creacion
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

        cursor.execute("""
            INSERT INTO intentos_formulario
            (id_usuario, id_formulario, estado)
            VALUES (?, ?, 'enviado')
        """, (id_usuario, id_formulario))

        id_intento = cursor.lastrowid

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

            elif tipo in ["opcion_unica", "opcion_multiple"]:
                opciones = respuesta.get("opciones", [])

                if pregunta["obligatoria"] and len(opciones) == 0:
                    raise ValueError(
                        f"La pregunta {id_pregunta} es obligatoria"
                    )

                if tipo == "opcion_unica" and len(opciones) > 1:
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

            if tipo in ["opcion_unica", "opcion_multiple"]:
                opciones = respuesta.get("opciones", [])

                for id_opcion in opciones:
                    cursor.execute("""
                        INSERT INTO respuestas_opciones
                        (id_respuesta, id_opcion)
                        VALUES (?, ?)
                    """, (id_respuesta, id_opcion))

        conn.commit()

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
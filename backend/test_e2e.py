import urllib.request
import urllib.error
import json
import uuid
import sys

BASE_URL = "http://127.0.0.1:5000/api"
V2_URL = f"{BASE_URL}/v2"
AUTH_URL = f"{BASE_URL}/auth"

def send_request(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    headers["Content-Type"] = "application/json"
    
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            resp_body = response.read().decode("utf-8")
            status = response.status
            return status, json.loads(resp_body) if resp_body else {}
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode("utf-8")
        return e.code, json.loads(resp_body) if resp_body else {}
    except Exception as e:
        print(f"Error connecting to {url}: {e}")
        sys.exit(1)

def run_tests():
    print("Iniciando pruebas E2E con urllib...")
    
    # 1. Registro
    email = f"test_{uuid.uuid4().hex[:6]}@example.com"
    pwd = "password123"
    print(f"\n[1] Registrando usuario: {email}")
    status, rjson = send_request(f"{AUTH_URL}/registro", method="POST", data={"nombre": "Tester", "correo": email, "password": pwd})
    if status != 201:
        print("FAIL Registro:", rjson)
        sys.exit(1)
    
    # 2. Login
    print("[2] Login de usuario")
    status, rjson = send_request(f"{AUTH_URL}/login", method="POST", data={"correo": email, "password": pwd})
    if status != 200:
        print("FAIL Login:", rjson)
        sys.exit(1)
    
    token = rjson.get("token")
    user_id = rjson.get("usuario", {}).get("id_usuario")
    headers = {"Authorization": f"Bearer {token}"}
    print(f"  -> OK! Token y UserID: {user_id}")

    # 3. Crear Cuestionario Publico
    print("\n[3] Crear Cuestionario Publico")
    payload_pub = {
        "titulo": "Test Publico",
        "descripcion": "desc",
        "visibilidad": "publico",
        "preguntas": [
            {"tipo": "texto_corto", "texto": "Pregunta texto pub", "obligatoria": True},
            {"tipo": "opcion_unica", "texto": "Pregunta opt pub", "obligatoria": True, "opciones": [{"texto": "O1", "valor": "O1"}, {"texto": "O2", "valor": "O2"}]}
        ]
    }
    status, rjson = send_request(f"{V2_URL}/formularios", method="POST", data=payload_pub, headers=headers)
    if status != 201:
        print("FAIL Crear Publico:", rjson)
        sys.exit(1)
    
    pub_code = rjson.get("codigo_compartir")
    pub_id = rjson.get("id_formulario")
    print(f"  -> OK! Codigo Publico: {pub_code} | ID: {pub_id}")

    # 4. Crear Cuestionario Privado
    print("\n[4] Crear Cuestionario Privado")
    payload_priv = {
        "titulo": "Test Privado",
        "descripcion": "desc priv",
        "visibilidad": "privado",
        "preguntas": [
            {"tipo": "texto_corto", "texto": "Pregunta texto priv", "obligatoria": True}
        ]
    }
    status, rjson = send_request(f"{V2_URL}/formularios", method="POST", data=payload_priv, headers=headers)
    if status != 201:
        print("FAIL Crear Privado:", rjson)
        sys.exit(1)
    
    priv_code = rjson.get("codigo_compartir")
    print(f"  -> OK! Codigo Privado: {priv_code}")

    # 5. Mis Formularios
    print("\n[5] Obtener Mis Formularios")
    status, rjson = send_request(f"{V2_URL}/formularios/mios", headers=headers)
    if status != 200:
        print("FAIL Mis Formularios:", rjson)
        sys.exit(1)
    
    mis_forms = rjson.get("formularios", [])
    if len(mis_forms) < 2:
        print("FAIL: Faltan formularios creados")
        sys.exit(1)
    print("  -> OK! Encontrados", len(mis_forms))

    # 6. Formularios Publicos (Explorar)
    print("\n[6] Obtener Formularios Publicos")
    status, rjson = send_request(f"{V2_URL}/formularios/publicos")
    if status != 200:
        print("FAIL Publicos:", rjson)
        sys.exit(1)
    
    pub_forms = rjson.get("formularios", [])
    codes_in_pub = [f["codigo_compartir"] for f in pub_forms]
    if pub_code not in codes_in_pub:
        print("FAIL: El formulario publico no esta en la lista publica")
        sys.exit(1)
    if priv_code in codes_in_pub:
        print("FAIL: El formulario PRIVADO se filtro a la lista publica!")
        sys.exit(1)
    print("  -> OK! La visibilidad funciona bien.")

    # 7. Obtener el formulario publico por codigo
    print("\n[7] Obtener formulario por codigo")
    status, rjson = send_request(f"{V2_URL}/formularios/codigo/{pub_code}")
    if status != 200:
        print("FAIL Get form:", rjson)
        sys.exit(1)
    form_full = rjson.get("formulario", {})
    preguntas_form = form_full.get("preguntas", [])
    print("  -> OK! Preguntas cargadas:", len(preguntas_form))
    id_p1 = preguntas_form[0]["id_pregunta"]
    id_p2 = preguntas_form[1]["id_pregunta"]
    opt_id = preguntas_form[1]["opciones"][0]["id_opcion"]

    # 8. Guardar Avance Parcial
    print("\n[8] Guardar avance parcial")
    avances = [
        {"id_pregunta": id_p1, "respuesta_texto": "Hola mundo test"}
    ]
    status, rjson = send_request(f"{V2_URL}/avance", method="POST", data={"id_usuario": user_id, "id_formulario": pub_id, "respuestas": avances})
    if status != 200:
        print("FAIL Guardar Avance:", rjson)
        sys.exit(1)
    print("  -> OK!")

    # 9. Recuperar Avance
    print("\n[9] Recuperar avance")
    status, rjson = send_request(f"{V2_URL}/avance/{user_id}/{pub_id}")
    if status != 200:
        print("FAIL Obtener Avance:", rjson)
        sys.exit(1)
    estado_intento = rjson.get("estado")
    if estado_intento != "en_progreso":
        print("FAIL Estado Intento no es en_progreso, es:", estado_intento)
        sys.exit(1)
    avances_recuperados = rjson.get("respuestas", [])
    if not avances_recuperados or avances_recuperados[0]["respuesta_texto"] != "Hola mundo test":
        print("FAIL Avance no se guardó correctamente:", avances_recuperados)
        sys.exit(1)
    print("  -> OK! Avance coincide.")

    # 10. Enviar Cuestionario (Final)
    print("\n[10] Enviar Cuestionario completo")
    respuestas_final = [
        {"id_pregunta": id_p1, "respuesta_texto": "Hola mundo final"},
        {"id_pregunta": id_p2, "opciones": [opt_id]}
    ]
    status, rjson = send_request(f"{BASE_URL}/respuestas", method="POST", data={"id_usuario": user_id, "id_formulario": pub_id, "respuestas": respuestas_final})
    if status != 201:
        print("FAIL Submit:", rjson)
        sys.exit(1)
    print("  -> OK!")

    # 11. Verificar Formularios Respondidos (Historial)
    print("\n[11] Obtener Respondidos (Historial)")
    status, rjson = send_request(f"{V2_URL}/formularios/respondidos/{user_id}")
    if status != 200:
        print("FAIL Respondidos:", rjson)
        sys.exit(1)
    respondidos = rjson.get("formularios", [])
    codes_resp = [f["codigo_compartir"] for f in respondidos]
    if pub_code not in codes_resp:
        print("FAIL: El formulario no aparece como respondido!")
        sys.exit(1)
    print("  -> OK! Aparece en historial.")

    # 12. Intentar recuperar avance tras enviar
    print("\n[12] Recuperar avance tras enviar (debe decir ya_enviado o estado=enviado)")
    status, rjson = send_request(f"{V2_URL}/avance/{user_id}/{pub_id}")
    estado_intento2 = rjson.get("estado")
    if estado_intento2 != "enviado":
        print("FAIL Estado no se actualizo a enviado, es:", estado_intento2)
        sys.exit(1)
    print("  -> OK! Bloqueado contra re-edición.")

    print("\n==============================================")
    print("🎉 TODAS LAS PRUEBAS E2E PASARON CORRECTAMENTE 🎉")
    print("==============================================")

if __name__ == "__main__":
    run_tests()

# Aplicación Web de Cuestionarios

Aplicación web desacoplada para crear, distribuir y analizar cuestionarios en línea.  
Proyecto Final — Desarrollo de Aplicaciones Web Desacopladas · IIMAS UNAM · 2026

**Equipo:** Alejandro Iram Ramírez Nava · Erick José Fabián Sandoval · Abril Minerva Estrada Montaño

---

## Stack

| Capa | Tecnología |
|---|---|
| Frontend | Vue 3 + TypeScript + Vite |
| Backend | Python + Flask |
| Base de datos | SQLite |
| Auth | Token Bearer (SHA-256) |

---

## Funcionalidades

- Registro e inicio de sesión con contraseña
- Crear cuestionarios con 7 tipos de pregunta: texto corto, texto largo, opción única, opción múltiple, escala 1–5, Sí/No y fecha
- Reordenar preguntas con botones ↑ ↓
- Editar cuestionarios (preguntas editables solo si no tienen respuestas aún)
- Archivar / publicar cuestionarios
- Compartir cuestionarios con código único de 10 caracteres
- Cuestionarios públicos o privados
- Guardado automático de avance al contestar
- Ver resultados con estadísticas: promedio, distribución por barras y listado de respuestas textuales

---

## Requisitos previos

- Python 3.10 o superior
- Node.js 18 o superior
- Git

---

## Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/0ElaLe/AplicacionCuestionarios.git
cd AplicacionCuestionarios
```

### 2. Configurar el backend

```bash
cd backend
python -m venv .venv
```

**Activar el entorno virtual:**

```bash
# Windows
.venv\Scripts\activate

```bash
pip install -r requirements.txt
```

### 3. Inicializar la base de datos

```bash
# Primero arranca Flask para crear las tablas, luego Ctrl+C para pararlo
python app.py

# Luego corre la migración
python migrate_v2.py
```

### 4. Arrancar el backend

```bash
python app.py
```

La API quedará disponible en: `http://localhost:5000`

---

### 5. Configurar e iniciar el frontend

Abre una segunda terminal desde la raíz del proyecto:

```bash
cd frontend-vue
npm install
npm run dev
```

El frontend quedará disponible en: `http://localhost:5173`

---

## Estructura del proyecto

```
├── backend/
│   ├── app.py              # Entrada de Flask
│   ├── modelo.py           # Acceso a datos y lógica de negocio
│   ├── v2_routes.py        # Rutas v2 (formularios, auth, resultados)
│   ├── auth_routes.py      # Registro e inicio de sesión
│   ├── rutas.py            # Rutas legacy (flujo anónimo)
│   ├── middleware.py       # Validación de token Bearer
│   ├── migrate_v2.py       # Migración de base de datos
│   └── requirements.txt
│
└── frontend-vue/
    └── src/
        ├── views/          # Vistas (Dashboard, Crear, Editar, Contestar, Resultados...)
        ├── components/
        │   └── questions/  # Componentes por tipo de pregunta
        ├── services/       # api.service.ts — comunicación con la API
        ├── composables/    # useAuth, useApp
        └── router/         # Rutas con guards de autenticación
```

---

## Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/auth/registro` | Registrar usuario |
| POST | `/api/auth/login` | Iniciar sesión |
| POST | `/api/v2/formularios` | Crear cuestionario |
| GET | `/api/v2/formularios/mios` | Mis cuestionarios |
| GET | `/api/v2/formularios/codigo/:codigo` | Obtener cuestionario por código |
| PUT | `/api/v2/formularios/:id` | Editar cuestionario |
| PATCH | `/api/v2/formularios/:id/archivar` | Archivar / publicar |
| GET | `/api/v2/formularios/:id/resultados` | Ver resultados y estadísticas |
| POST | `/api/respuestas` | Guardar respuestas |
| POST | `/api/v2/avance` | Guardar avance parcial |

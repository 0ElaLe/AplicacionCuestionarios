# Aplicación de Cuestionarios V2

Una aplicación web desacoplada para la creación, distribución y resolución de cuestionarios dinámicos.

## Arquitectura

*   **Frontend**: Vue 3 + TypeScript + Vite.
*   **Backend**: Python + Flask.
*   **Base de Datos**: SQLite3.

## Novedades en V2

*   **Autenticación JWT**: Sistema de login y registro de usuarios.
*   **Formularios Dinámicos**: Crea cuestionarios interactivos con 5 tipos de preguntas:
    *   Texto corto
    *   Texto largo
    *   Opción única
    *   Opción múltiple
    *   Escala (1-5)
*   **Gestión de Cuestionarios**: 
    *   Mis cuestionarios (Creados por ti).
    *   Cuestionarios Públicos (Explorar).
    *   Historial (Cuestionarios respondidos).
*   **Guardado Automático (Avance)**: El progreso de los usuarios se guarda automáticamente para evitar pérdida de datos si cierran la página antes de enviar el cuestionario.
*   **Privacidad**: Opción de crear cuestionarios Públicos o Privados (solo accesibles con el código único).

## Estructura del Proyecto

```
/
├── backend/
│   ├── app.py                      # Punto de entrada principal Flask
│   ├── modelo.py                   # Acceso a base de datos (SQLite)
│   ├── v2_routes.py                # Endpoints de la API v2
│   ├── schema.sql                  # Esquema inicial
│   ├── migrate_v2.py               # Script de migración de base de datos a V2
│   ├── seed_cuestionario_prueba.py # Script de poblamiento de prueba
│   └── test_e2e.py                 # Script de pruebas end-to-end
│
└── frontend-vue/
    ├── src/
    │   ├── components/             # Componentes reusables de UI y preguntas
    │   ├── composables/            # Lógica de estado compartida (useAuth, etc.)
    │   ├── services/               # Llamadas a la API y configuración HTTP
    │   ├── views/                  # Páginas principales (Dashboard, Crear, Contestar)
    │   └── assets/                 # Estilos globales y tokens
    └── package.json                # Dependencias Node.js
```

## Ejecución Local

### 1. Iniciar el Backend (Terminal 1)

```bash
cd backend

# 1. Instalar dependencias
pip install flask flask-cors pyjwt requests

# 2. Inicializar la base de datos (Ejecutar solo la primera vez)
python init_db.py

# 3. Levantar el servidor
python app.py
```

### 2. Iniciar el Frontend (Terminal 2)

```bash
cd frontend-vue
npm install
npm run dev
```

La aplicación estará disponible en [http://localhost:5173](http://localhost:5173).

## Pruebas (E2E)
Para verificar la integridad de la API de manera automática:
```bash
cd backend
python test_e2e.py
```

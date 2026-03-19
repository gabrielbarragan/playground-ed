# ofline_playground

Plataforma educativa de programación Python con editor en tiempo real, ejecución segura en sandbox, sistema de retos, evaluaciones y panel de seguimiento para docentes.

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12 · FastAPI 0.129 · Uvicorn 0.40 (standard) |
| Base de datos | MongoDB 7 · MongoEngine 0.29 |
| Autenticación | JWT (python-jose) · PBKDF2-HMAC-SHA256 |
| Frontend | Vue 3 · TypeScript · Vite · Pinia · Vue Router · Axios |
| Editor | Monaco Editor |
| Terminal | XTerm.js (WebSocket streaming) |
| Infraestructura | Docker Compose · nginx · Let's Encrypt (certbot) |
| Hosting | Hetzner VPS (CX22) · DuckDNS |

---

## Funcionalidades

### Para estudiantes
- **Playground Python** — editor Monaco con resaltado de sintaxis, ejecución interactiva vía WebSocket (soporta `input()`), terminal XTerm.js con streaming en tiempo real
- **Snippets** — guardar, cargar y eliminar fragmentos de código personales
- **Retos** — lista de desafíos por curso con evaluación automática por test cases; soporte para revisión manual por el docente
- **Evaluaciones (Quizzes)** — cuestionarios de opción múltiple con puntaje, barra de progreso y resultado detallado por pregunta
- **Dashboard personal** — heatmap de actividad de los últimos 15 días, racha de días, ranking del curso con posición propia resaltada

### Para docentes (Admin)
- **Panel de usuarios** — tabla completa con búsqueda, filtro por curso, ordenamiento por nombre / puntos / último acceso / fecha de registro, activar/desactivar alumnos
- **Gestión de cursos** — crear cursos, activar/desactivar
- **Gestión de retos** — crear/editar retos con test cases, dificultad, puntaje y revisión manual; revisar entregas pendientes
- **Gestión de evaluaciones** — crear quizzes con preguntas y opciones inline, ver resultados por alumno, resetear intentos
- **Stats globales** — usuarios activos/inactivos, ejecuciones últimos 7 días, activos esta semana

### Para superadmin
- Gestión de roles (student → admin → superadmin)
- CRUD de cursos con visibilidad de inactivos

---

## Arquitectura

```
Puerto 443 (HTTPS)
  └── nginx
        ├── /          → frontend Vue (dist/)
        ├── /api/      → backend FastAPI :8000
        └── /ws/       → WebSocket FastAPI :8000

backend (FastAPI)
  └── app/
        ├── api/<módulo>/{views, process, querysets, serializer}
        ├── core/      auth · sandbox · constants
        ├── config/    routers · settings
        └── models/    User · Course · CodeSnippet · CodeActivity
                       Challenge · ChallengeAttempt · Reward

MongoDB (interno)  ← volumen persistente mongo_data
```

### Sandbox de ejecución

- Subprocess aislado con entorno limpio (solo `PATH`, `HOME=/tmp`)
- Límites: CPU 10s · archivo 1 MB · procesos hijos 10
- HTTP: timeout 10s · output máx. 50 KB
- WebSocket: sesión máx. 120s · soporta `stdin` en tiempo real y señal `kill`

### Autenticación

- OAuth2 Password Flow; el campo `username` del form recibe el email
- Token JWT en `localStorage`; interceptor Axios inyecta `Authorization: Bearer` en cada request
- Redirect automático a `/login` en respuestas 401

### Jerarquía de roles

| Rol | `is_admin` | `is_superadmin` | Acceso |
|---|---|---|---|
| student | false | false | Playground, Dashboard, Retos, Evaluaciones |
| admin (Docente) | true | false | + Panel Admin |
| superadmin | true | true | + Panel Superadmin (gestión de roles) |

---

## Inicio rápido (desarrollo local)

### Prerrequisitos

- Docker y Docker Compose
- Node 22+ (solo para desarrollo frontend sin Docker)

### 1. Variables de entorno

```bash
cp .env.example .env
# Editar .env — mínimo requerido:
# JWT_SECRET=<string aleatorio>
# MONGO_URI se define internamente en el compose
```

### 2. Levantar con Docker

```bash
docker compose up -d --build
```

Servicios disponibles:
- Frontend: `http://localhost`
- Backend API: `http://localhost/api/v1/`
- Health check: `http://localhost/api/health`

### 3. Primer usuario admin

Registrar una cuenta desde `/register`, luego promoverla en MongoDB:

```bash
docker compose exec mongo \
  mongosh playground --eval '
    db.users.updateOne(
      { email: "docente@example.com" },
      { $set: { is_admin: true } }
    )
  '
```

Para superadmin:

```bash
docker compose exec mongo \
  mongosh playground --eval '
    db.users.updateOne(
      { email: "super@example.com" },
      { $set: { is_admin: true, is_superadmin: true } }
    )
  '
```

---

## Deploy en producción (Hetzner + HTTPS)

### Primera vez

```bash
# 1. En el servidor — instalar Docker y UFW
bash scripts/setup-server.sh

# 2. Clonar el repo
git clone <repo_url> /opt/ofline_playground
cd /opt/ofline_playground

# 3. Crear .env
cat > .env <<EOF
JWT_SECRET=$(openssl rand -hex 32)
JWT_EXPIRE_MINUTES=1440
DOMAIN=miapp.duckdns.org
EMAIL=mi@email.com
EOF

# 4. Obtener certificado SSL y levantar producción
export DOMAIN=miapp.duckdns.org
export EMAIL=mi@email.com
bash scripts/init-ssl.sh
```

> `init-ssl.sh` reemplaza `${DOMAIN}` en la config nginx, obtiene el certificado con certbot y levanta todos los servicios con HTTPS. Luego ejecutar `git update-index --skip-worktree frontend/nginx.prod.conf` para evitar conflictos en futuros pulls.

### Redeploy (aplicar cambios)

```bash
bash scripts/deploy.sh   # git pull + rebuild + prune
```

### Variables de entorno requeridas en producción

| Variable | Descripción |
|---|---|
| `JWT_SECRET` | Clave secreta JWT — `openssl rand -hex 32` |
| `JWT_EXPIRE_MINUTES` | Expiración del token en minutos (default: 1440) |
| `DOMAIN` | Dominio del servidor (ej: `miapp.duckdns.org`) |
| `EMAIL` | Email para el certificado Let's Encrypt |

`MONGO_URI` se define internamente en el compose: `mongodb://mongo:27017/playground`

---

## Migraciones de base de datos

MongoEngine es estricto: si se agrega un campo nuevo al modelo, los documentos existentes deben migrarse antes del redeploy. Ejemplo:

```bash
docker compose -f docker-compose.prod.yml exec mongo \
  mongosh playground --eval '
    db.users.updateMany(
      { nuevo_campo: { $exists: false } },
      { $set: { nuevo_campo: false } }
    )
  '
```

---

## Protocolo WebSocket

```
Cliente → Servidor
  { "type": "run",   "code": "..." }      ← iniciar ejecución
  { "type": "stdin", "data": "...\n" }    ← responder input()
  { "type": "kill" }                      ← forzar terminación

Servidor → Cliente
  { "type": "stdout",  "data": "..." }
  { "type": "stderr",  "data": "..." }
  { "type": "exit",    "return_code": 0 }
  { "type": "timeout" }
  { "type": "error",   "message": "..." }
```

Auth opcional: `ws://host/ws/run?token=<JWT>`

---

## API — endpoints principales

| Método | Endpoint | Auth | Descripción |
|---|---|---|---|
| POST | `/api/v1/auth/register` | — | Registro de usuario |
| POST | `/api/v1/auth/login` | — | Login → `{access_token}` |
| GET | `/api/v1/users/me` | requerida | Perfil del usuario |
| GET | `/api/v1/dashboard/activity` | requerida | Heatmap de actividad |
| GET | `/api/v1/dashboard/courses/{id}/ranking` | — | Ranking del curso |
| GET/POST/PUT/DELETE | `/api/v1/snippets/` | requerida | CRUD de snippets |
| GET | `/api/v1/admin/users` | admin | Listar usuarios |
| GET | `/api/v1/admin/stats` | admin | Stats globales |
| POST | `/api/code-runs` | opcional | Ejecución HTTP (sin input) |
| WS | `/ws/run` | opcional | Ejecución interactiva |
| GET | `/api/health` | — | Health check |

---

## Estructura del proyecto

```
ofline_playground/
├── app/                        # Backend FastAPI
│   ├── api/
│   │   ├── admin/              # Panel docente
│   │   ├── superadmin/         # Gestión de roles
│   │   ├── auth/ · users/      # Autenticación y perfil
│   │   ├── courses/            # Cursos
│   │   ├── snippets/           # Snippets de código
│   │   ├── dashboard/          # Actividad y ranking
│   │   ├── challenges/         # Retos y entregas
│   │   ├── quizzes/            # Evaluaciones
│   │   └── v1/                 # Sandbox HTTP + WebSocket
│   ├── core/                   # Auth · Sandbox · Constants
│   ├── config/                 # Routers · Settings
│   └── models/                 # Modelos MongoEngine
├── frontend/
│   └── src/
│       ├── features/           # Vistas por módulo (playground, admin, dashboard…)
│       ├── api/                # Clientes Axios por módulo
│       ├── stores/             # Estado global Pinia
│       ├── router/             # Vue Router + guards
│       └── types/              # Interfaces TypeScript
├── scripts/
│   ├── setup-server.sh         # Preparar servidor Ubuntu
│   ├── init-ssl.sh             # Obtener SSL + levantar producción
│   └── deploy.sh               # Redeploy
├── docker-compose.yml          # Compose HTTP (desarrollo/testing)
├── docker-compose.prod.yml     # Compose HTTPS producción
├── docker-compose.bootstrap.yml
├── Dockerfile.backend
├── frontend/Dockerfile.frontend
└── .env.example
```

---

## Tema visual

[Catppuccin Mocha](https://github.com/catppuccin/catppuccin) — `bg: #1e1e2e` · `surface: #181825` · `border: #313244` · `accent: #cba6f7`
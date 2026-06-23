# Playground ED — Resumen de Funcionalidades

Plataforma educativa para la enseanza de programacion en Python. Los estudiantes escriben y ejecutan codigo en un editor Monaco integrado en el navegador, con ejecucion en tiempo real via WebSocket en un sandbox seguro. Incluye retos, quizzes, snippets, dashboards y paneles de administracion para docentes.

---

## Roles y Permisos

La plataforma maneja tres niveles de acceso con permisos acumulativos:

```
Estudiante ──▶ Docente (Admin) ──▶ Superadmin
```

| Capacidad | Estudiante | Docente | Superadmin |
|---|:---:|:---:|:---:|
| Ejecutar codigo en el playground | ✔ | ✔ | ✔ |
| Resolver retos y quizzes | ✔ | ✔ | ✔ |
| Guardar snippets de codigo | ✔ | ✔ | ✔ |
| Ver dashboard personal | ✔ | ✔ | ✔ |
| Desbloquear logros | ✔ | ✔ | ✔ |
| Cambiar badge personal | ✔ | ✔ | ✔ |
| Crear/editar retos y quizzes | | ✔ | ✔ |
| Revisar envios manuales | | ✔ | ✔ |
| Gestionar estudiantes y cursos | | ✔ | ✔ |
| Ver analiticas globales | | ✔ | ✔ |
| Promover/degradar roles de usuario | | | ✔ |
| Gestion global de usuarios | | | ✔ |

---

## Playground Interactivo

El nucleo de la plataforma es un IDE en el navegador con las siguientes caracteristicas:

```
┌─────────────────────────────────────────────────────────┐
│  Playground ED                          [Badge] [User]  │
├──────────┬──────────────────────────┬───────────────────┤
│          │                          │                   │
│  Panel   │     Editor Monaco        │   Panel Derecho   │
│  Izq.    │                          │                   │
│          │  - Syntax highlighting   │  - Descripcion    │
│ - Retos  │  - Autocompletado        │    del reto       │
│ - Snippets│  - Multiples lenguajes  │  - Casos de       │
│ - Logros │  - Ctrl+Enter = Run      │    prueba         │
│          │                          │  - Ejemplo I/O    │
│          ├──────────────────────────┤                   │
│          │     Terminal             │                   │
│          │  - stdout / stderr       │                   │
│          │  - Input interactivo     │                   │
│          │  - Canvas grafico        │                   │
│          │  - Estado del servidor   │                   │
└──────────┴──────────────────────────┴───────────────────┘
```

### Ejecucion de Codigo

Dos modos de ejecucion disponibles:

| Modo | Protocolo | Input interactivo | Timeout | Uso |
|---|---|:---:|---|---|
| Directo | HTTP POST | No | 10s | Ejecucion rapida sin `input()` |
| Interactivo | WebSocket | Si | 120s | Sesiones con `input()` y streaming |

**Limites del sandbox:**

| Recurso | Limite |
|---|---|
| Tiempo de CPU | 10 segundos |
| Tamano de archivo | 1 MB |
| Procesos hijos | 10 |
| Salida maxima | 50 KB |
| Sesion WebSocket | 120 segundos |

**Protocolo WebSocket:**

```
Cliente → Servidor              Servidor → Cliente
─────────────────               ──────────────────
{type: "run",  code: "..."}     {type: "stdout", data: "..."}
{type: "stdin", data: "...\n"}  {type: "stderr", data: "..."}
{type: "kill"}                  {type: "exit", return_code: 0}
                                {type: "timeout"}
                                {type: "gfx", data: {...}}
                                {type: "achievement", data: {...}}
```

---

## Sistema de Retos

Los retos son ejercicios de programacion con evaluacion automatica y/o revision manual.

### Flujo de un reto

```
Estudiante escribe codigo
        │
        ▼
Validacion AST (funciones requeridas)
        │
        ▼
Ejecucion contra test cases
        │
        ├── Todos pasan + sin revision manual ──▶ Puntos otorgados
        │
        └── requires_review = true ──▶ Pendiente de aprobacion docente
                                              │
                                        Aprobado ──▶ Puntos otorgados
                                        Rechazado ──▶ Feedback al estudiante
```

### Estructura de un reto

| Campo | Descripcion |
|---|---|
| Titulo y descripcion | Enunciado del problema (soporta Markdown) |
| Dificultad | `easy`, `medium`, `hard` |
| Cursos | Uno o varios cursos asignados |
| Codigo inicial | Plantilla de partida para el estudiante |
| Ejemplo I/O | Entrada/salida ilustrativa (no se ejecuta) |
| Test cases | Pares entrada/salida para evaluacion automatica |
| Test cases ocultos | No visibles para el estudiante |
| Puntos | Valor base del reto |
| Funciones requeridas | Validacion AST obligatoria |
| Bono de eficiencia | Puntos extra si el codigo esta dentro de un rango de lineas |
| Revision manual | Si el docente debe aprobar aunque los tests pasen |

### Multiplicador por intento

El sistema incentiva resolver el reto en los primeros intentos:

| Intento | Multiplicador | Ejemplo (reto de 100 pts) |
|---|---|---|
| 1ro | 100% | 100 pts |
| 2do | 75% | 75 pts |
| 3ro | 50% | 50 pts |
| 4to | 25% | 25 pts |
| 5to+ | 10% | 10 pts |

> Minimo 1 punto si el reto tiene puntos base > 0.

---

## Sistema de Quizzes

Evaluaciones de opcion multiple con soporte para bloques de codigo en las preguntas.

### Configuracion del quiz

| Campo | Descripcion |
|---|---|
| Titulo y descripcion | Nombre y contexto del quiz |
| Puntaje de aprobacion | Minimo de respuestas correctas para aprobar |
| Puntos por completar | Se otorgan al enviar (apruebe o no) |
| Puntos por aprobar | Bonus adicional solo si aprueba |
| Mostrar respuestas | Si el estudiante ve las correctas despues de enviar |
| Banco aleatorio | Selecciona N preguntas al azar del pool |

### Banco de preguntas aleatorio

Cuando esta activo, cada estudiante recibe un subconjunto determinista de preguntas:

```
Pool de 20 preguntas
        │
        ▼
Seed = hash(user_id + quiz_id)
        │
        ▼
Seleccion de 10 preguntas (siempre las mismas para ese estudiante)
```

### Flujo del quiz

```
Estudiante abre quiz
        │
        ▼
Responde preguntas (opcion multiple)
        │
        ▼
Envia respuestas (intento unico)
        │
        ├── correctas >= passing_score ──▶ points_on_complete + points_on_pass
        │
        └── correctas < passing_score  ──▶ points_on_complete
        │
        ▼
Feedback (si show_correct_answers = true):
  - Respuesta correcta por pregunta
  - Explicacion del docente
```

> El docente puede resetear el intento de un estudiante sin revertir los puntos ya otorgados.

---

## Snippets de Codigo

Biblioteca personal de fragmentos de codigo reutilizables.

| Caracteristica | Detalle |
|---|---|
| Campos | Titulo, codigo, lenguaje, tags |
| Visibilidad | Publica o privada (privada por defecto) |
| Acceso | Solo el propietario puede editar/eliminar |
| Integracion | Se pueden cargar directamente en el editor desde el panel lateral |

---

## Dashboard y Analiticas

### Dashboard del estudiante

```
┌─────────────────────────────────────────────┐
│  Dashboard Personal                         │
├─────────────┬───────────────────────────────┤
│             │                               │
│  Racha:     │  Heatmap de actividad         │
│  5 dias     │  (ultimos 15 dias)            │
│             │                               │
│  Total      │  ██ ██ ░░ ██ ██ ██ ░░ ...    │
│  ejec: 142  │                               │
│             │  Ejecuciones por dia           │
│  Puntos:    │  Lineas escritas por dia       │
│  450        │  Tasa de exito                 │
│             │                               │
└─────────────┴───────────────────────────────┘
```

### Analiticas del docente

| Metrica | Alcance |
|---|---|
| Usuarios activos/inactivos | Global |
| Ejecuciones (ultimos 7 dias) | Global |
| Resumen por curso | Usuarios, actividad, puntos |
| Heatmap por estudiante | Ultimos 15 dias por alumno |
| Ranking del curso | Top N estudiantes por puntos |
| Progreso en retos | Por estudiante |
| Resultados de quizzes | Por estudiante y por clase |

---

## Gamificacion

### Sistema de puntos

Los puntos se acumulan de multiples fuentes y alimentan el ranking del curso:

```
                    ┌─────────────────┐
                    │  total_points   │
                    │  (ranking)      │
                    └────────▲────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
    ┌─────┴──────┐    ┌──────┴──────┐    ┌──────┴──────┐
    │  Retos     │    │  Quizzes    │    │  Logros     │
    │ base × mul │    │ completar   │    │ bonus pts   │
    │ + bono     │    │ + aprobar   │    │             │
    │ eficiencia │    │             │    │             │
    └────────────┘    └─────────────┘    └─────────────┘
```

### Logros (Sandbox Achievements)

Se desbloquean automaticamente al detectar conceptos de programacion en el codigo ejecutado (analisis AST):

| Logro | Concepto detectado | Bonus |
|---|---|---|
| Bucle While | `while` loop | Variable |
| Try/Except | Manejo de excepciones | Variable |
| List Comprehension | Comprension de listas | Variable |
| Clases | Definicion de `class` | Variable |
| Lambdas | Funciones `lambda` | Variable |
| Generadores | `yield` / generadores | Variable |
| Recursion | Llamada recursiva | Variable |
| Combo | Lambda + List Comprehension | Variable |

> Cada logro se desbloquea una sola vez por usuario y se notifica en tiempo real via WebSocket.

### Badges

Los usuarios eligen un emoji como badge personal que se muestra junto a su nombre en la plataforma.

### Recompensas (Rewards)

Capa adicional de incentivos basada en hitos:

| Trigger | Descripcion |
|---|---|
| `challenges_completed` | Completar N retos |
| `streak_days` | Mantener racha de N dias |
| `points_total` | Alcanzar N puntos totales |
| `first_snippet` | Guardar el primer snippet |

---

## Panel de Administracion (Docente)

El panel del docente organiza la gestion en pestanas:

```
┌──────────────────────────────────────────────────────┐
│  Panel Docente                                       │
├──────────┬──────────┬─────────┬──────────┬───────────┤
│  Retos   │ Envios   │ Cursos  │ Usuarios │ Analitica │
└──────────┴──────────┴─────────┴──────────┴───────────┘
```

| Pestana | Funcionalidades |
|---|---|
| **Retos** | Crear, editar, activar/desactivar retos. Gestionar test cases. Filtrar por dificultad. |
| **Envios** | Revisar envios pendientes de aprobacion manual. Aprobar/rechazar con feedback. Ver codigo y resultados de tests. |
| **Cursos** | Crear cursos con codigo y descripcion. Activar/desactivar cursos. |
| **Usuarios** | Listar estudiantes por curso. Activar/desactivar cuentas. Cambiar email directamente. |
| **Analitica** | Estadisticas globales. Actividad por curso. Rankings. Heatmaps por estudiante. |

---

## Panel de Superadmin

| Funcionalidad | Descripcion |
|---|---|
| Gestion global de usuarios | Buscar y filtrar todos los usuarios del sistema |
| Cambio de roles | Promover/degradar entre Estudiante, Docente y Superadmin |
| Gestion de cursos | Crear y administrar todos los cursos |
| Proteccion | No puede degradar su propio rol |

---

## Autenticacion y Seguridad

### Flujos de autenticacion

```
Registro ──▶ Login ──▶ JWT Token ──▶ Acceso a rutas protegidas
                          │
                     Expira en 24h
                     (configurable)
```

| Caracteristica | Detalle |
|---|---|
| Hashing de passwords | PBKDF2-HMAC-SHA256, 260k iteraciones, salt de 32 bytes |
| Tokens JWT | HS256, expiracion configurable (default 24h) |
| Comparacion de passwords | Tiempo constante (`hmac.compare_digest`) |
| Proteccion contra enumeracion | `/forgot-password` siempre retorna 200 |
| Tokens de un solo uso | Hash SHA256 almacenado, limpiado tras uso |

### Recuperacion de contrasena

```
Solicitud ──▶ Email con token (15 min) ──▶ Nueva contrasena
```

### Cambio de email

```
Solicitud ──▶ Email de confirmacion (30 min) ──▶ Email actualizado
```

> Los docentes pueden cambiar el email de un estudiante directamente sin confirmacion.

---

## Rutas de la Aplicacion

| Ruta | Acceso | Vista |
|---|---|---|
| `/login` | Publica | Inicio de sesion |
| `/register` | Publica | Registro con seleccion de curso |
| `/forgot-password` | Publica | Solicitud de recuperacion |
| `/reset-password` | Publica | Formulario de nueva contrasena |
| `/` | Autenticado | Playground (IDE principal) |
| `/dashboard` | Autenticado | Dashboard personal |
| `/quizzes` | Autenticado | Lista y ejecucion de quizzes |
| `/profile` | Autenticado | Perfil y configuracion |
| `/confirm-email` | Autenticado | Confirmacion de cambio de email |
| `/admin` | Docente | Panel de administracion |
| `/superadmin` | Superadmin | Panel de superadministrador |

# Gestión de Cursos para Docentes y Solicitud de Cambio de Curso

## Problema

Actualmente existen dos limitaciones importantes en la gestión de cursos:

1. **Estudiantes sin movilidad de curso**: Un estudiante pertenece a un único curso (campo `course` en User, `ReferenceField` required) asignado al registrarse. No existe mecanismo para cambiar de curso. Si un estudiante necesita moverse, requiere intervención directa en la base de datos.

2. **Docentes sin restricción de cursos**: Cualquier usuario con rol `admin` (docente) puede ver todos los cursos, todos los estudiantes y revisar todos los envíos de la plataforma. No hay forma de limitar a un docente a ver solo los estudiantes y envíos de los cursos que imparte.

## Objetivo

### Parte A — Solicitud de cambio de curso (Estudiante → Docente)

Permitir que un estudiante solicite cambio de curso desde su perfil. La solicitud queda pendiente hasta que un docente con acceso a ese curso la apruebe o rechace. Al aprobar, el campo `course` del estudiante se actualiza automáticamente.

### Parte B — Asignación de cursos a docentes (Superadmin)

Permitir al superadmin asignar qué cursos puede gestionar cada docente. Un docente solo ve los estudiantes, envíos, retos y estadísticas de los cursos que tiene asignados. El superadmin mantiene acceso global.

## Estado Actual

### Modelo User

```python
class User(Document):
    course = ReferenceField("Course", required=True)  # un solo curso, sin cambio
    is_admin = BooleanField(default=False)
    is_superadmin = BooleanField(default=False)
```

- No existe campo para almacenar los cursos asignados a un docente.
- No existe modelo para solicitudes de cambio de curso.

### Backend — Admin

- `GET /api/v1/admin/users` (`admin/process.py:33-43`): lista usuarios filtrable por `course_id`, pero no filtra por los cursos del docente autenticado — muestra todos.
- `GET /api/v1/admin/stats` (`admin/process.py:125-157`): estadísticas globales de todos los cursos, sin filtro por docente.
- El guard `get_current_admin` solo verifica `is_admin=True`, no qué cursos tiene asignados.

### Backend — Superadmin

- `PUT /api/v1/superadmin/users/{userId}/role` (`superadmin/process.py:54-66`): cambia rol, pero no gestiona asignación de cursos al docente.
- No hay endpoint para asignar/desasignar cursos a un docente.

### Frontend — Admin

- `AdminView.vue`: tabs Usuarios, Cursos, Retos, Revisiones, Evaluaciones, Logros, Analítica. La lista de usuarios y cursos no filtra por cursos del docente.

### Frontend — Superadmin

- `SuperAdminView.vue`: tabs Usuarios y Cursos. La tabla de usuarios muestra un `<select>` para cambiar roles, pero no hay UI para asignar cursos a docentes.

### Frontend — Perfil del estudiante

- No hay opción de solicitar cambio de curso.

## Cambios Propuestos

### Parte A — Solicitud de cambio de curso

#### Nuevo modelo: `CourseChangeRequest`

```python
class CourseChangeRequest(Document):
    user = ReferenceField("User", required=True)
    from_course = ReferenceField("Course", required=True)
    to_course = ReferenceField("Course", required=True)
    reason = StringField(default="")
    status = StringField(default="pending", choices=["pending", "approved", "rejected"])
    resolved_by = ReferenceField("User", null=True)
    resolved_at = DateTimeField(null=True)
    rejection_reason = StringField(default="")
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "course_change_requests",
        "indexes": ["user", "status", ("user", "status")],
    }
```

#### Backend

1. **Endpoint estudiante** — `POST /api/v1/users/me/course-change-request`:
   - Body: `{ to_course_id: str, reason?: str }`.
   - Valida que el curso destino exista y esté activo.
   - Valida que no exista una solicitud pendiente del mismo estudiante.
   - Valida que el curso destino sea diferente al actual.
   - Crea un `CourseChangeRequest` con `status="pending"`.

2. **Endpoint estudiante** — `GET /api/v1/users/me/course-change-request`:
   - Retorna la solicitud pendiente del estudiante (si existe), o `null`.
   - Incluye nombre del curso destino y fecha de creación.

3. **Endpoint docente** — `GET /api/v1/admin/course-change-requests`:
   - Lista solicitudes pendientes de los cursos que el docente tiene asignados (origen o destino).
   - Incluye datos del estudiante, curso origen, curso destino, razón y fecha.

4. **Endpoint docente** — `PUT /api/v1/admin/course-change-requests/{requestId}/resolve`:
   - Body: `{ action: "approve" | "reject", rejection_reason?: str }`.
   - Si `approve`: actualiza `user.course` al `to_course`, marca la solicitud como `approved`.
   - Si `reject`: marca como `rejected` con razón opcional.
   - Registra `resolved_by` y `resolved_at`.

#### Frontend — Perfil del estudiante

1. En la vista de perfil (`ProfileView.vue`), agregar sección "Mi curso" que muestre:
   - Curso actual del estudiante.
   - Botón "Solicitar cambio de curso" que abre un formulario/modal.
   - Si ya tiene solicitud pendiente: mostrar estado "Pendiente de aprobación" con el curso solicitado.

2. Modal/formulario de solicitud:
   - Selector de curso destino (cursos activos, excluyendo el actual).
   - Campo opcional de razón.
   - Botón "Enviar solicitud".

#### Frontend — Panel Admin

1. Nueva tab "Solicitudes" en `AdminView.vue` (o integrar en tab Usuarios):
   - Lista de solicitudes pendientes de cambio de curso.
   - Cada solicitud muestra: nombre del estudiante, curso actual, curso solicitado, razón, fecha.
   - Botones "Aprobar" y "Rechazar" por solicitud.
   - Al rechazar, campo para razón de rechazo (opcional).

### Parte B — Asignación de cursos a docentes

#### Cambio en modelo User

Agregar campo `assigned_courses` al modelo `User`:

```python
assigned_courses = ListField(ReferenceField("Course"), default=list)
```

- Solo aplica a usuarios con `is_admin=True`.
- Lista vacía = sin restricción (para no romper docentes existentes, pero se debe poblar al asignar).
- El superadmin no usa este campo — tiene acceso global por diseño.

**Migración**: antes de desplegar, ejecutar en `mongosh`:
```js
db.users.updateMany(
  { assigned_courses: { $exists: false } },
  { $set: { assigned_courses: [] } }
)
```

#### Backend — Superadmin

1. **Endpoint** — `PUT /api/v1/superadmin/users/{userId}/courses`:
   - Body: `{ course_ids: [str] }`.
   - Valida que el usuario sea admin.
   - Valida que todos los `course_ids` existan.
   - Actualiza `user.assigned_courses`.
   - Retorna el usuario serializado con los cursos asignados.

2. **Serialización**: agregar `assigned_courses` a la serialización de usuario en superadmin.

#### Backend — Admin (filtrado por cursos asignados)

1. **Modificar `get_current_admin`** o crear un helper `get_admin_course_ids(ctx)`:
   - Si el usuario es superadmin, retorna `None` (sin filtro).
   - Si el usuario es admin con `assigned_courses` no vacío, retorna esos IDs.
   - Si el usuario es admin con `assigned_courses` vacío, retorna lista vacía (no ve nada hasta que el superadmin le asigne cursos).

2. **Filtrar endpoints del admin**:
   - `GET /api/v1/admin/users`: solo mostrar estudiantes cuyo `course` esté en los cursos asignados del docente.
   - `GET /api/v1/admin/stats`: solo mostrar estadísticas de los cursos asignados del docente.
   - `GET /api/v1/admin/course-change-requests`: solo solicitudes donde el curso origen o destino esté en los cursos del docente.
   - Los endpoints de perfil de estudiante (`/api/v1/admin/users/{userId}/...`): validar que el estudiante pertenezca a un curso del docente.
   - Endpoints de revisión de envíos: filtrar por cursos del docente.

3. **No afectar**: creación/edición de retos y quizzes (esos se asignan a cursos específicos, el docente selecciona los cursos al crear). Listar cursos del admin puede limitarse a sus cursos asignados.

#### Frontend — Superadmin

1. En la tabla de usuarios, agregar columna "Cursos" visible solo para usuarios con rol `admin`:
   - Mostrar los cursos asignados como badges.
   - Al hacer click, abrir modal/popover para seleccionar/deseleccionar cursos.

2. Modal de asignación de cursos:
   - Lista de cursos activos con checkboxes.
   - Botón "Guardar" que llama a `PUT /api/v1/superadmin/users/{userId}/courses`.

#### Frontend — Admin

- No requiere cambios directos en la UI — el filtrado ocurre en backend.
- Los selectores de curso en la vista admin solo mostrarán los cursos que el backend retorna (que ya estarán filtrados).

## Archivos a Crear/Modificar

### Nuevos archivos

| Archivo | Descripción |
|---|---|
| `app/models/course_change_request.py` | Modelo `CourseChangeRequest` |
| `app/api/course_requests/views.py` | Endpoints de solicitud de cambio (estudiante) |
| `app/api/course_requests/process.py` | Lógica de negocio de solicitudes |
| `app/api/course_requests/querysets.py` | Queries MongoDB para solicitudes |
| `app/api/course_requests/serializer.py` | Serializers Pydantic |
| `frontend/src/api/courseRequestsApi.ts` | API client para solicitudes |
| `frontend/src/features/admin/components/CourseRequestsPanel.vue` | Panel de solicitudes en admin |
| `frontend/src/features/superadmin/components/AdminCourseAssignModal.vue` | Modal de asignación de cursos en superadmin |

### Archivos a modificar

| Archivo | Cambio |
|---|---|
| `app/models/__init__.py` | Registrar `CourseChangeRequest` |
| `app/models/user.py` | Agregar campo `assigned_courses` |
| `app/config/routers.py` | Registrar router de `course_requests` |
| `app/api/admin/process.py` | Filtrar `list_users()` y `get_global_stats()` por cursos del docente |
| `app/api/admin/views.py` | Pasar `ctx` a funciones que necesiten filtrar por cursos |
| `app/api/admin/student_views.py` | Validar que el estudiante pertenezca a un curso del docente |
| `app/api/admin/querysets.py` | Agregar filtros por lista de cursos |
| `app/api/challenges/views.py` | Pasar `admin_course_ids` al filtrar envíos pendientes |
| `app/api/superadmin/views.py` | Agregar endpoint de asignación de cursos |
| `app/api/superadmin/process.py` | Lógica de asignación de cursos, serializar `assigned_courses` |
| `app/core/auth.py` | Helper `get_admin_course_ids()` o extender `UserContext` |
| `frontend/src/api/superAdminApi.ts` | Agregar `assignCourses()`, extender tipo con `assigned_courses` |
| `frontend/src/features/profile/ProfileView.vue` | Sección "Mi curso" con botón de solicitud |
| `frontend/src/features/admin/AdminView.vue` | Agregar tab/sección de solicitudes de cambio de curso |
| `frontend/src/features/superadmin/SuperAdminView.vue` | Columna de cursos asignados y modal de asignación |

## Tasks

### Parte B — Asignación de cursos a docentes (implementar primero)

#### Modelo y migración

- [x] **B-1**: Agregar campo `assigned_courses = ListField(ReferenceField("Course"), default=list)` al modelo `User`
- [x] **B-2**: Documentar migración `mongosh`: `db.users.updateMany({ assigned_courses: { $exists: false } }, { $set: { assigned_courses: [] } })`

#### Backend — Superadmin

- [x] **B-3**: Agregar endpoint `PUT /api/v1/superadmin/users/{userId}/courses` con body `{ course_ids: [str] }` — valida que el usuario sea admin y que los cursos existan, actualiza `assigned_courses`
- [x] **B-4**: Extender serialización de usuario en superadmin para incluir `assigned_courses` con id, name y code de cada curso

#### Backend — Filtrado del admin

- [x] **B-5**: Crear helper `get_admin_course_ids(ctx: UserContext) -> list[str] | None` — retorna `None` para superadmin (sin filtro), lista de IDs para admin
- [x] **B-6**: Modificar `list_users()` en `admin/process.py` para filtrar estudiantes por cursos del docente
- [x] **B-7**: Modificar `get_global_stats()` en `admin/process.py` para filtrar estadísticas por cursos del docente
- [x] **B-8**: Agregar validación en endpoints de perfil de estudiante (`admin/student_views.py`) para verificar que el estudiante pertenezca a un curso del docente
- [x] **B-9**: Filtrar envíos pendientes de revisión por cursos del docente

#### Frontend — Superadmin

- [x] **B-10**: Extender tipo `SuperAdminUser` en `superAdminApi.ts` con campo `assigned_courses`
- [x] **B-11**: Agregar método `assignCourses(userId, courseIds)` en `superAdminApi.ts`
- [x] **B-12**: Mostrar columna/badges de cursos asignados en tabla de usuarios de `SuperAdminView.vue` (solo para rol admin)
- [x] **B-13**: Crear modal `AdminCourseAssignModal.vue` con checkboxes de cursos activos y botón guardar
- [x] **B-14**: Integrar modal en `SuperAdminView.vue` — abrir al hacer click en los badges de cursos de un docente

### Parte A — Solicitud de cambio de curso

#### Modelo

- [x] **A-1**: Crear modelo `CourseChangeRequest` en `app/models/course_change_request.py`
- [x] **A-2**: Registrar modelo en `app/models/__init__.py`

#### Backend — Estudiante

- [x] **A-3**: Crear `app/api/course_requests/querysets.py` con métodos: `create_request()`, `get_pending_by_user()`, `get_pending_by_courses()`, `resolve_request()`
- [x] **A-4**: Crear `app/api/course_requests/process.py` con lógica: `create_change_request()`, `get_my_pending_request()`, `list_pending_requests()`, `resolve_request()`
- [x] **A-5**: Crear `app/api/course_requests/serializer.py` con `CreateRequestSerializer` y `ResolveRequestSerializer`
- [x] **A-6**: Crear `app/api/course_requests/views.py` con endpoints: `POST /me/course-change-request`, `GET /me/course-change-request`
- [x] **A-7**: Registrar router en `app/config/routers.py`

#### Backend — Docente

- [x] **A-8**: Agregar endpoint `GET /api/v1/admin/course-change-requests` — lista solicitudes pendientes filtradas por cursos del docente
- [x] **A-9**: Agregar endpoint `PUT /api/v1/admin/course-change-requests/{requestId}/resolve` — aprueba o rechaza, actualiza `user.course` al aprobar

#### Frontend — Estudiante

- [x] **A-10**: Crear `courseRequestsApi.ts` con `createRequest()`, `getMyPendingRequest()`
- [x] **A-11**: Agregar sección "Mi curso" en `ProfileView.vue` — muestra curso actual y botón "Solicitar cambio"
- [x] **A-12**: Agregar modal/formulario de solicitud: selector de curso destino, campo razón, botón enviar
- [x] **A-13**: Mostrar estado de solicitud pendiente si existe (curso solicitado, fecha, "Pendiente de aprobación")

#### Frontend — Docente

- [x] **A-14**: Agregar `listPendingRequests()` y `resolveRequest()` a API client del admin
- [x] **A-15**: Crear `CourseRequestsPanel.vue` — lista solicitudes con datos del estudiante, cursos, razón, botones aprobar/rechazar
- [x] **A-16**: Integrar panel en `AdminView.vue` como nueva tab o sección dentro de tab Usuarios

#### Validación

- [ ] **QA-1**: Verificar que un estudiante puede solicitar cambio de curso y aparece como pendiente
- [ ] **QA-2**: Verificar que un estudiante no puede crear dos solicitudes pendientes simultáneas
- [ ] **QA-3**: Verificar que el docente ve solo solicitudes de sus cursos asignados
- [ ] **QA-4**: Verificar que al aprobar, el curso del estudiante cambia efectivamente
- [ ] **QA-5**: Verificar que al rechazar, el estudiante puede crear una nueva solicitud
- [ ] **QA-6**: Verificar que un docente sin cursos asignados no ve estudiantes ni solicitudes
- [ ] **QA-7**: Verificar que el superadmin puede asignar/desasignar cursos a docentes
- [ ] **QA-8**: Verificar que el superadmin mantiene acceso global sin restricción de cursos

## Requerimientos (Gherkin)

```gherkin
Feature: Asignación de cursos a docentes
  Como superadmin
  Quiero asignar qué cursos puede gestionar cada docente
  Para que cada docente solo vea los estudiantes y envíos de sus cursos

  Background:
    Given existen los cursos "PY2024", "PY2025" y "INTRO2024" activos
    And existe un docente "Prof. García"
    And existe un superadmin autenticado

  # ── Asignación ────────────────────────────────────────────

  Scenario: Superadmin asigna cursos a un docente
    When el superadmin asigna los cursos "PY2024" y "PY2025" al docente "Prof. García"
    Then el endpoint responde con el usuario actualizado
    And el campo assigned_courses contiene "PY2024" y "PY2025"

  Scenario: Superadmin puede reasignar cursos
    Given "Prof. García" tiene asignados "PY2024" y "PY2025"
    When el superadmin cambia la asignación a solo "INTRO2024"
    Then assigned_courses contiene solo "INTRO2024"

  Scenario: Solo se pueden asignar cursos a usuarios con rol admin
    When el superadmin intenta asignar cursos a un estudiante
    Then el backend responde con HTTP 400
    And el mensaje indica que solo se pueden asignar cursos a docentes

  # ── Filtrado del admin ────────────────────────────────────

  Scenario: Docente solo ve estudiantes de sus cursos
    Given "Prof. García" tiene asignado el curso "PY2024"
    And existen estudiantes en "PY2024" y en "PY2025"
    When "Prof. García" consulta la lista de usuarios
    Then solo ve los estudiantes del curso "PY2024"
    And no ve los estudiantes de "PY2025"

  Scenario: Docente solo ve estadísticas de sus cursos
    Given "Prof. García" tiene asignado el curso "PY2024"
    When consulta las estadísticas globales
    Then solo aparecen datos del curso "PY2024"

  Scenario: Docente sin cursos asignados no ve estudiantes
    Given "Prof. García" tiene assigned_courses vacío
    When consulta la lista de usuarios
    Then la lista está vacía

  Scenario: Docente no puede ver perfil de estudiante de otro curso
    Given "Prof. García" tiene asignado solo "PY2024"
    And el estudiante "Ana" pertenece al curso "PY2025"
    When intenta consultar el perfil de "Ana"
    Then el backend responde con HTTP 403

  Scenario: Superadmin mantiene acceso global
    Given el superadmin no tiene assigned_courses
    When consulta la lista de usuarios
    Then ve todos los estudiantes de todos los cursos

  # ── Envíos de revisión ────────────────────────────────────

  Scenario: Docente solo ve envíos de revisión de sus cursos
    Given "Prof. García" tiene asignado "PY2024"
    And hay envíos pendientes de estudiantes de "PY2024" y "PY2025"
    When consulta los envíos pendientes de revisión
    Then solo ve los envíos de estudiantes de "PY2024"

Feature: Solicitud de cambio de curso
  Como estudiante
  Quiero solicitar un cambio de curso
  Para moverme a otro grupo sin intervención directa en la base de datos

  Background:
    Given el estudiante "Juan" está autenticado
    And "Juan" pertenece al curso "PY2024"
    And existen los cursos activos "PY2024" y "PY2025"

  # ── Crear solicitud ──────────────────────────────────────

  Scenario: Estudiante solicita cambio de curso
    When "Juan" envía una solicitud de cambio al curso "PY2025" con razón "Cambio de horario"
    Then se crea una solicitud con status "pending"
    And la solicitud tiene from_course="PY2024" y to_course="PY2025"

  Scenario: Estudiante no puede solicitar cambio al mismo curso
    When "Juan" intenta solicitar cambio al curso "PY2024" (su curso actual)
    Then el backend responde con HTTP 400
    And el mensaje indica que no puede solicitar cambio al mismo curso

  Scenario: Estudiante no puede tener dos solicitudes pendientes
    Given "Juan" ya tiene una solicitud pendiente
    When intenta crear otra solicitud
    Then el backend responde con HTTP 409
    And el mensaje indica que ya tiene una solicitud pendiente

  Scenario: Estudiante no puede solicitar cambio a un curso inactivo
    Given el curso "INACTIVO" existe pero está desactivado
    When "Juan" intenta solicitar cambio al curso "INACTIVO"
    Then el backend responde con HTTP 400

  Scenario: Estudiante puede ver su solicitud pendiente
    Given "Juan" tiene una solicitud pendiente hacia "PY2025"
    When consulta su solicitud pendiente
    Then recibe los datos de la solicitud con status "pending"

  Scenario: Estudiante sin solicitud pendiente recibe null
    Given "Juan" no tiene solicitudes pendientes
    When consulta su solicitud pendiente
    Then recibe null

  # ── Resolución por docente ───────────────────────────────

  Scenario: Docente aprueba solicitud de cambio de curso
    Given "Juan" tiene solicitud pendiente hacia "PY2025"
    And el docente tiene asignados los cursos "PY2024" y "PY2025"
    When el docente aprueba la solicitud
    Then la solicitud pasa a status "approved"
    And el campo course de "Juan" cambia a "PY2025"
    And se registran resolved_by y resolved_at

  Scenario: Docente rechaza solicitud con razón
    Given "Juan" tiene solicitud pendiente hacia "PY2025"
    When el docente rechaza la solicitud con razón "El curso ya está lleno"
    Then la solicitud pasa a status "rejected"
    And el campo course de "Juan" sigue siendo "PY2024"
    And la solicitud tiene rejection_reason "El curso ya está lleno"

  Scenario: Estudiante puede crear nueva solicitud tras rechazo
    Given "Juan" tenía solicitud pendiente que fue rechazada
    When crea una nueva solicitud de cambio de curso
    Then se crea exitosamente con status "pending"

  Scenario: Docente solo ve solicitudes de sus cursos
    Given el docente tiene asignado solo "PY2024"
    And existen solicitudes de cambio desde "PY2024" y desde "INTRO2024"
    When consulta las solicitudes pendientes
    Then solo ve las solicitudes donde "PY2024" es curso origen o destino
```

## Notas

- **Orden de implementación**: Parte B primero (asignación de cursos a docentes), luego Parte A (solicitudes de cambio). La Parte A depende de B para filtrar qué solicitudes ve cada docente.
- **Docentes existentes**: al agregar `assigned_courses`, los docentes existentes tendrán lista vacía. El superadmin deberá asignarles cursos después del deploy. Mientras la lista esté vacía, no verán estudiantes — esto es intencional para forzar la configuración.
- **Migración MongoDB**: se necesita un `updateMany` para agregar el campo `assigned_courses` a los documentos existentes antes del deploy.
- **Superadmin no se filtra**: el superadmin nunca se filtra por `assigned_courses`. Su acceso es global por diseño.
- **El campo `course` del User sigue siendo required**: un estudiante siempre pertenece a un curso. El cambio solo modifica a qué curso pertenece.
- **Impacto en rankings/puntos**: al cambiar de curso, los puntos del estudiante se conservan. El ranking del curso nuevo lo incluirá automáticamente porque se basa en `user.course`.

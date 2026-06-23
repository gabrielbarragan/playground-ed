# Filtros y Ordenamiento en Revisión de Envíos

## Problema

El panel de revisión de envíos (`SubmissionsPanel.vue`) muestra todos los envíos pendientes en una lista plana ordenada por fecha de envío. No hay forma de filtrar ni ordenar, lo que dificulta la revisión cuando hay muchos envíos acumulados.

## Objetivo

Permitir al docente filtrar por **reto** y por **curso**, y ordenar por **nombre del estudiante**, **reto** o **puntos base**, para agilizar la revisión manual.

## Estado Actual

### Backend

- `GET /api/v1/admin/submissions/pending` acepta `challenge_id` como query param opcional (`views.py:138-147`).
- El queryset `AttemptQueryset.get_pending_review()` consulta `review_status="pending"` ordenado por `submitted_at` (`querysets.py:32-34`).
- El filtro por `challenge_id` se aplica en Python después de la consulta, no en la query de Mongo (`process.py:261-266`).
- **No existe** filtro por curso.
- La serialización del attempt ya incluye `challenge.title`, `challenge.difficulty`, `challenge.points` y `user.first_name`, `user.last_name` (`process.py:68-111`).

### Frontend

- `SubmissionsPanel.vue` llama a `challengesApi.pendingSubmissions()` sin parámetros y renderiza `submissions` tal cual llegan.
- No hay ningún control de filtro ni selector de ordenamiento.
- `challengesApi.pendingSubmissions(challengeId?)` ya soporta enviar `challenge_id` al backend.

## Cambios Propuestos

### Backend

1. **Agregar filtro por `course_id`** al endpoint `GET /api/v1/admin/submissions/pending`:
   - Nuevo query param: `course_id: Optional[str]`.
   - Filtrar en el queryset (o en process) los attempts cuyo `challenge.courses` incluya el curso indicado.

2. **Agregar parámetro de ordenamiento** `sort_by`:
   - Valores posibles: `date` (default), `student_name`, `challenge_title`, `points`.
   - Dirección: `sort_dir` = `asc` | `desc`.
   - Ordenar en Python post-query (el volumen de pending reviews es bajo, no justifica índices Mongo adicionales).

3. **Incluir cursos del reto en la serialización del attempt** (`_serialize_attempt`):
   - Agregar `challenge.courses: [{id, name, code}]` al dict serializado, para que el frontend pueda armar el dropdown de cursos sin una llamada extra.

### Frontend

1. **Barra de filtros** encima de la lista en `SubmissionsPanel.vue`:
   - Dropdown "Filtrar por curso" — alimentado con los cursos extraídos de los submissions cargados.
   - Dropdown "Filtrar por reto" — alimentado con los retos extraídos de los submissions cargados. Si se selecciona un curso, solo mostrar retos de ese curso.
   - Ambos filtros se aplican client-side sobre los datos ya cargados.

2. **Controles de ordenamiento**:
   - Botones o headers clickeables para ordenar por: nombre del estudiante, título del reto, puntos base.
   - Toggle ascendente/descendente.
   - Ordenamiento client-side.

3. **Contador dinámico**: actualizar el texto "N envío(s) pendiente(s)" para reflejar el total filtrado.

## Archivos a Modificar

| Archivo | Cambio |
|---|---|
| `app/api/challenges/views.py` | Agregar query params `course_id`, `sort_by`, `sort_dir` al endpoint `/pending` |
| `app/api/challenges/process.py` | Implementar filtro por curso y ordenamiento en `list_pending_reviews()`, agregar cursos a `_serialize_attempt()` |
| `frontend/src/features/admin/components/SubmissionsPanel.vue` | UI de filtros y ordenamiento client-side |
| `frontend/src/api/challengesApi.ts` | Extender `pendingSubmissions()` para aceptar `courseId` |

## Tasks

- [x] **BE-1**: Agregar `course_id` como query param opcional al endpoint `GET /api/v1/admin/submissions/pending` en `views.py`
- [x] **BE-2**: Implementar filtro por curso en `list_pending_reviews()` de `process.py` (filtrar attempts cuyo reto pertenezca al curso indicado)
- [x] **BE-3**: Incluir `challenge.courses: [{id, name, code}]` en la serialización de `_serialize_attempt()` en `process.py`
- [x] **BE-4**: Agregar parámetros `sort_by` y `sort_dir` al endpoint `/pending` en `views.py` y pasarlos a `list_pending_reviews()`
- [x] **BE-5**: Implementar ordenamiento en `list_pending_reviews()` por `date`, `student_name`, `challenge_title`, `points` con dirección `asc`/`desc`
- [x] **FE-1**: Crear barra de filtros en `SubmissionsPanel.vue` con dropdown de curso y dropdown de reto
- [x] **FE-2**: Extraer opciones de curso y reto a partir de los submissions cargados (computed). Filtrar retos visibles según curso seleccionado
- [x] **FE-3**: Implementar filtrado client-side de submissions según curso y reto seleccionados
- [x] **FE-4**: Agregar controles de ordenamiento (nombre estudiante, título reto, puntos base) con toggle asc/desc
- [x] **FE-5**: Implementar ordenamiento client-side con `computed` sobre la lista filtrada
- [x] **FE-6**: Actualizar contador dinámico "N envío(s) pendiente(s)" para reflejar el total filtrado vs. total real
- [x] **FE-7**: Extender `pendingSubmissions()` en `challengesApi.ts` para aceptar `courseId` como parámetro opcional
- [x] **QA-1**: Verificar manualmente filtros, ordenamiento y contador en el panel de envíos con datos de prueba

## Requerimientos (Gherkin)

```gherkin
Feature: Filtros y ordenamiento en revisión de envíos
  Como docente
  Quiero filtrar y ordenar los envíos pendientes de revisión
  Para encontrar y revisar envíos de forma más eficiente

  Background:
    Given el docente está autenticado
    And existen envíos pendientes de revisión de múltiples estudiantes, retos y cursos

  # ── Filtro por curso ──────────────────────────────────────────

  Scenario: Filtrar envíos por curso
    Given hay envíos pendientes del curso "Python Básico" y del curso "Python Avanzado"
    When el docente selecciona el curso "Python Básico" en el filtro de curso
    Then solo se muestran los envíos de retos que pertenecen al curso "Python Básico"
    And el contador muestra la cantidad de envíos filtrados

  Scenario: Limpiar filtro de curso
    Given el docente tiene el filtro de curso activo en "Python Básico"
    When el docente selecciona la opción "Todos los cursos"
    Then se muestran todos los envíos pendientes sin filtrar por curso

  # ── Filtro por reto ───────────────────────────────────────────

  Scenario: Filtrar envíos por reto
    Given hay envíos pendientes de los retos "Hola Mundo" y "Fibonacci"
    When el docente selecciona el reto "Fibonacci" en el filtro de reto
    Then solo se muestran los envíos correspondientes al reto "Fibonacci"
    And el contador muestra la cantidad de envíos filtrados

  Scenario: Filtro de reto se adapta al curso seleccionado
    Given el reto "Hola Mundo" pertenece al curso "Python Básico"
    And el reto "Fibonacci" pertenece al curso "Python Avanzado"
    When el docente selecciona el curso "Python Básico" en el filtro de curso
    Then el dropdown de reto solo muestra "Hola Mundo" como opción

  Scenario: Limpiar filtro de reto
    Given el docente tiene el filtro de reto activo en "Fibonacci"
    When el docente selecciona la opción "Todos los retos"
    Then se muestran todos los envíos pendientes (respetando el filtro de curso si está activo)

  # ── Combinación de filtros ────────────────────────────────────

  Scenario: Aplicar filtro de curso y reto simultáneamente
    Given hay envíos de múltiples retos y cursos
    When el docente selecciona el curso "Python Básico"
    And selecciona el reto "Hola Mundo"
    Then solo se muestran los envíos del reto "Hola Mundo" del curso "Python Básico"

  Scenario: Cambiar filtro de curso resetea el filtro de reto
    Given el docente tiene filtro de curso "Python Básico" y filtro de reto "Hola Mundo"
    When el docente cambia el filtro de curso a "Python Avanzado"
    Then el filtro de reto se resetea a "Todos los retos"
    And se muestran todos los envíos del curso "Python Avanzado"

  # ── Ordenamiento ──────────────────────────────────────────────

  Scenario: Ordenar envíos por nombre de estudiante ascendente
    When el docente selecciona ordenar por "Nombre del estudiante" en dirección ascendente
    Then los envíos se muestran ordenados alfabéticamente por nombre del estudiante de A a Z

  Scenario: Ordenar envíos por nombre de estudiante descendente
    Given los envíos están ordenados por nombre ascendente
    When el docente hace click en el toggle de dirección
    Then los envíos se muestran ordenados de Z a A

  Scenario: Ordenar envíos por título de reto
    When el docente selecciona ordenar por "Reto"
    Then los envíos se agrupan visualmente por reto en orden alfabético

  Scenario: Ordenar envíos por puntos base
    When el docente selecciona ordenar por "Puntos"
    Then los envíos se muestran ordenados por los puntos base del reto de mayor a menor

  Scenario: Ordenamiento se mantiene al filtrar
    Given el docente tiene ordenamiento por nombre de estudiante ascendente
    When aplica un filtro de curso
    Then los envíos filtrados se muestran respetando el ordenamiento activo

  # ── Contador dinámico ─────────────────────────────────────────

  Scenario: Contador refleja el total filtrado
    Given hay 15 envíos pendientes en total
    And 6 pertenecen al curso "Python Básico"
    When el docente selecciona el curso "Python Básico"
    Then el contador muestra "6 envío(s) pendiente(s)"

  Scenario: Contador sin filtros muestra el total real
    Given hay 15 envíos pendientes en total
    And no hay filtros activos
    Then el contador muestra "15 envío(s) pendiente(s)"

  # ── Estado vacío ──────────────────────────────────────────────

  Scenario: Sin resultados después de filtrar
    Given hay envíos pendientes pero ninguno del curso "Curso Vacío"
    When el docente selecciona el curso "Curso Vacío"
    Then se muestra el mensaje "No hay envíos pendientes de revisión."
    And el contador muestra "0 envío(s) pendiente(s)"
```

## Notas

- El filtro por reto ya existe en el backend (vía `challenge_id`), pero no se usa en el frontend. Se puede reutilizar.
- El volumen de envíos pendientes suele ser bajo (decenas, no miles), así que el filtrado/ordenamiento client-side es suficiente y evita complejidad en el backend. El filtro server-side por `course_id` es útil si a futuro se necesita paginación.

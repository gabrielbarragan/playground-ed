# Ver Snippet de Estudiante en el Editor

## Problema

Desde el panel de administración, al abrir el perfil de un estudiante y ver la pestaña "Snippets", solo se muestra un listado con el título, lenguaje, tags y un preview de 3 líneas del código (`StudentSnippetsPanel.vue`). No hay forma de ver el código completo de un snippet ni de cargarlo en el editor para revisarlo. El endpoint actual (`GET /api/v1/admin/users/{userId}/snippets`) no devuelve el campo `code` completo, solo `code_preview`.

## Objetivo

Permitir al docente hacer click en un snippet de un estudiante desde el drawer de perfil y que el código completo se cargue en el editor del Playground en **modo solo lectura**, con una barra visible que indique el nombre del snippet y el nombre del estudiante al que pertenece.

## Estado Actual

### Backend

- `GET /api/v1/admin/users/{userId}/snippets` (`student_views.py:54-63`) retorna una lista de snippets con `code_preview` (3 primeras líneas), no el `code` completo (`student_profile.py:255-274`).
- No existe un endpoint para obtener un snippet individual de un estudiante.
- El modelo `CodeSnippet` (`models/code_snippet.py`) tiene el campo `code` con el código completo.

### Frontend

- `StudentSnippetsPanel.vue`: renderiza snippets en grid con título, lenguaje, preview y tags. No tiene evento de click ni interacción.
- `StudentProfileDrawer.vue`: drawer lateral con tabs, se abre desde `AdminView.vue`.
- `PlaygroundView.vue`: contiene el Monaco editor que carga código vía `store.code`. Ya soporta cargar snippets propios a través de `SnippetsPanel.vue` + `useSnippetsStore`.
- `usePlaygroundStore.ts`: estado `code` (ref) que se bindea al editor vía v-model.
- `useSnippetsStore.ts`: maneja `activeSnippet` para snippets propios del usuario. El botón "Actualizar" aparece cuando hay un `activeSnippet` activo.
- `useStudentProfileStore.ts`: maneja el estado del drawer del perfil del estudiante. Tiene `userId` y `summary` (que contiene `first_name`, `last_name` del alumno).

### Flujo actual de carga de snippet propio

1. Usuario clickea "Mis Snippets" → abre `SnippetsPanel.vue`.
2. Clickea un snippet → `snippetsStore.load(snippet)` setea `activeSnippet` y retorna `code`.
3. `PlaygroundView` recibe el código y setea `store.code = code`.
4. El editor se actualiza vía v-model.

## Cambios Propuestos

### Backend

1. **Nuevo endpoint**: `GET /api/v1/admin/users/{userId}/snippets/{snippetId}` que retorne un snippet individual con el código completo.
   - Validar que el snippet pertenezca al usuario indicado.
   - Retornar: `id`, `title`, `code`, `language`, `tags`, `created_at`, `updated_at`.

### Frontend

1. **Hacer clickeables los snippet cards** en `StudentSnippetsPanel.vue`:
   - Al hacer click en un snippet card, emitir un evento `view-snippet` con el `snippetId`.
   - Agregar cursor pointer y efecto hover al card para indicar que es interactivo.

2. **Propagar el evento desde el drawer hasta el Playground**:
   - `StudentSnippetsPanel` emite `view-snippet(snippetId)` → `StudentProfileDrawer` lo propaga → `AdminView` recibe el evento.
   - `AdminView` navega al Playground con query params: `/playground?viewSnippet={snippetId}&studentId={userId}`.
   - Alternativamente, si el docente ya está en el Playground, se puede usar un store compartido en vez de navegación.

3. **Nuevo estado en `usePlaygroundStore`**: `viewingStudentSnippet`
   - Objeto nullable: `{ snippetTitle, studentName, code }`.
   - Cuando está activo, el editor carga ese código en **modo solo lectura** (desactiva edición y oculta botones de guardar/actualizar/enviar).
   - Un botón "Cerrar vista" limpia el estado y restaura el editor al código previo del docente.

4. **Barra indicadora en el editor** (dentro de `PlaygroundView.vue`):
   - Cuando `viewingStudentSnippet` está activo, mostrar una barra encima del editor con:
     - Nombre del snippet y nombre del estudiante (ej: "Fibonacci — Juan Pérez").
     - Botón para cerrar la vista y volver al código propio.
   - Estilo visual diferenciado (fondo de color distinto) para que sea claro que se está viendo código ajeno.

5. **Fetch del código completo**:
   - Cuando se activa la vista, llamar al nuevo endpoint `GET /api/v1/admin/users/{userId}/snippets/{snippetId}` para obtener el `code` completo.
   - Agregar el método `getSnippetDetail(userId, snippetId)` a `studentProfileApi.ts`.

## Archivos a Crear/Modificar

| Archivo | Cambio |
|---|---|
| `app/api/admin/student_views.py` | Nuevo endpoint `GET /{userId}/snippets/{snippetId}` |
| `app/api/admin/student_profile.py` | Nueva función `get_student_snippet_detail()` que retorne snippet con código completo |
| `frontend/src/api/studentProfileApi.ts` | Agregar `getSnippetDetail(userId, snippetId)` |
| `frontend/src/features/admin/components/StudentSnippetsPanel.vue` | Hacer cards clickeables, emitir `view-snippet` |
| `frontend/src/features/admin/components/StudentProfileDrawer.vue` | Propagar evento `view-snippet` |
| `frontend/src/features/admin/AdminView.vue` | Manejar evento y navegar al Playground con query params |
| `frontend/src/stores/usePlaygroundStore.ts` | Agregar estado `viewingStudentSnippet` y acción para activar/limpiar |
| `frontend/src/features/playground/PlaygroundView.vue` | Leer query params, mostrar barra indicadora, modo solo lectura |

## Tasks

### Backend

- [ ] **BE-1**: Crear función `get_student_snippet_detail(user_id, snippet_id)` en `student_profile.py` que retorne un snippet individual con `code` completo, validando que pertenezca al usuario
- [ ] **BE-2**: Registrar endpoint `GET /api/v1/admin/users/{userId}/snippets/{snippetId}` en `student_views.py`

### Frontend — API y estado

- [ ] **FE-1**: Agregar `getSnippetDetail(userId, snippetId)` a `studentProfileApi.ts`
- [ ] **FE-2**: Agregar estado `viewingStudentSnippet` a `usePlaygroundStore` con acciones `setStudentSnippetView(snippetTitle, studentName, code)` y `clearStudentSnippetView()`

### Frontend — Panel de snippets

- [ ] **FE-3**: Hacer clickeables los snippet cards en `StudentSnippetsPanel.vue`, emitir evento `view-snippet` con `snippetId`
- [ ] **FE-4**: Propagar evento `view-snippet` en `StudentProfileDrawer.vue` hacia `AdminView.vue`
- [ ] **FE-5**: En `AdminView.vue`, manejar el evento navegando al Playground con query params `viewSnippet` y `studentId`

### Frontend — Editor

- [ ] **FE-6**: En `PlaygroundView.vue`, leer query params al montar, llamar al endpoint para obtener el snippet completo, y activar `viewingStudentSnippet`
- [ ] **FE-7**: Mostrar barra indicadora encima del editor con título del snippet, nombre del estudiante, y botón "Cerrar vista"
- [ ] **FE-8**: Cuando `viewingStudentSnippet` está activo, poner el editor en solo lectura y ocultar botones de guardar/actualizar/enviar reto
- [ ] **FE-9**: Al cerrar la vista, restaurar el código previo del docente y limpiar query params

### Validación

- [ ] **QA-1**: Verificar que al clickear un snippet de estudiante se navega al Playground y se muestra el código completo con la barra indicadora
- [ ] **QA-2**: Verificar que el editor está en solo lectura y no se pueden usar botones de guardar/actualizar
- [ ] **QA-3**: Verificar que al cerrar la vista se restaura el código anterior del docente
- [ ] **QA-4**: Verificar que un snippet de un estudiante no puede ser consultado por otro estudiante (solo admin)

## Notas

- Se usa navegación con query params (`/playground?viewSnippet=...&studentId=...`) para que funcione tanto si el docente ya está en el Playground como si viene del panel admin. También permite compartir el link directo.
- El código previo del docente se debe guardar antes de cargar el snippet del estudiante, para restaurarlo al cerrar la vista.
- El `activeSnippet` de `useSnippetsStore` NO se debe modificar al ver un snippet de estudiante — son flujos independientes.
- El modo solo lectura debe desactivar: edición en Monaco, botón "Guardar", botón "Actualizar", botón "Enviar" (reto).

# Changelog

## Asignación de cursos a docentes y solicitud de cambio de curso

- **Fecha**: 2026-06-24
- **Rama**: `feature/snippets-students-in-editor`

### Cambios

#### Asignación de cursos a docentes (Superadmin)

- feat(model): agregar campo `assigned_courses` (ListField de ReferenceField a Course) en modelo `User`
- feat(api): agregar helper `get_admin_course_ids()` en `auth.py` y campo `assigned_course_ids` en `UserContext`
- feat(api): agregar endpoint `PUT /api/v1/superadmin/users/{userId}/courses` para asignar cursos a docentes
- feat(api): extender serialización de usuario en superadmin para incluir `assigned_courses`
- feat(api): filtrar `list_users()` en `admin/process.py` por cursos asignados del docente
- feat(api): filtrar `get_global_stats()` en `admin/process.py` por cursos asignados del docente
- feat(api): agregar validación `_check_student_access()` en todos los endpoints de `student_views.py` (HTTP 403 si el docente no tiene acceso al curso del estudiante)
- feat(api): filtrar envíos pendientes de revisión por cursos del docente en `challenges/process.py`
- feat(frontend): extender tipo `SuperAdminUser` con campo `assigned_courses` en `superAdminApi.ts`
- feat(frontend): agregar método `assignCourses()` en `superAdminApi.ts`
- feat(frontend): agregar columna "Cursos asignados" con badges en tabla de usuarios de `SuperAdminView.vue`
- feat(frontend): crear modal `AdminCourseAssignModal.vue` con checkboxes de cursos activos

#### Solicitud de cambio de curso (Estudiante → Docente)

- feat(model): crear modelo `CourseChangeRequest` con campos user, from_course, to_course, reason, status, resolved_by, rejection_reason
- feat(api): crear módulo `app/api/course_requests/` con querysets, process, serializer y views
- feat(api): agregar endpoint `POST /api/v1/users/me/course-change-request` para crear solicitud
- feat(api): agregar endpoint `GET /api/v1/users/me/course-change-request` para consultar solicitud pendiente
- feat(api): agregar endpoint `GET /api/v1/admin/course-change-requests` para listar solicitudes filtradas por cursos del docente
- feat(api): agregar endpoint `PUT /api/v1/admin/course-change-requests/{requestId}/resolve` para aprobar o rechazar
- feat(frontend): crear API client `courseRequestsApi.ts` con createRequest, getMyPendingRequest, listPendingRequests, resolveRequest
- feat(frontend): agregar sección "Mi curso" en `ProfileView.vue` con formulario de solicitud y estado pendiente
- feat(frontend): crear `CourseRequestsPanel.vue` con lista de solicitudes, botones aprobar/rechazar y campo de razón de rechazo
- feat(frontend): agregar tab "Solicitudes" en `AdminView.vue`

---

## Ver snippet de estudiante en el editor

- **Fecha**: 2026-06-24
- **Rama**: `feature/snippets-students-in-editor`

### Cambios

- feat(api): agregar función `get_student_snippet_detail()` en `student_profile.py` para obtener snippet individual con código completo
- feat(api): registrar endpoint `GET /api/v1/admin/users/{userId}/snippets/{snippetId}` en `student_views.py`
- feat(frontend): agregar `getSnippetDetail(userId, snippetId)` en `studentProfileApi.ts`
- feat(frontend): agregar estado `viewingStudentSnippet` con acciones `setStudentSnippetView()` y `clearStudentSnippetView()` en `usePlaygroundStore`
- feat(frontend): hacer clickeables los snippet cards en `StudentSnippetsPanel.vue` con evento `view-snippet`
- feat(frontend): propagar evento `view-snippet` desde `StudentProfileDrawer` hasta `AdminView`
- feat(frontend): navegar al Playground con query params `viewSnippet` y `studentId` desde `AdminView`
- feat(frontend): leer query params en `PlaygroundView`, cargar snippet completo y activar modo solo lectura
- feat(frontend): mostrar banner indicador con título del snippet, nombre del estudiante y botón "Cerrar vista"
- feat(frontend): ocultar botones de guardar/actualizar/enviar en modo vista de snippet
- feat(frontend): agregar prop `readOnly` con watcher dinámico en `MonacoEditor`

## Bloqueo de pegado y drag & drop en el editor

- **Fecha**: 2026-06-24
- **Rama**: `feature/snippets-students-in-editor`

### Cambios

- feat(frontend): bloquear `drop` y `dragover` en el contenedor del editor Monaco
- feat(frontend): bloquear `beforeinput` con tipos `insertFromPaste` e `insertFromDrop`
- feat(frontend): bloquear atajo `Shift+Insert` como método alternativo de pegado

---

## Bloqueo de reenvío de retos resueltos o pendientes

- **Fecha**: 2026-06-22
- **Rama**: `feature/filtros-revision-envios`

### Cambios

- feat(api): agregar guard en `submit_challenge()` que bloquea envíos a retos ya aprobados
- feat(api): agregar guard en `submit_challenge()` que bloquea envíos a retos con revisión pendiente
- feat(api): agregar método `has_pending_review()` en `AttemptQueryset`
- feat(frontend): agregar computed `canSubmit` y `activeStatus` en `useChallengesStore`
- feat(frontend): condicionar botón "Enviar" con texto dinámico ("Resuelto ✓" / "En revisión ⏳") en `PlaygroundView`
- feat(frontend): agregar banner de estado en `ChallengeDescription` cuando el reto está bloqueado

---

## Filtros y ordenamiento en revisión de envíos

- **Fecha**: 2026-06-22
- **Rama**: `feature/filtros-revision-envios`

### Cambios

- feat(api): agregar filtros por curso y ordenamiento en endpoint de envíos pendientes
- feat(api): incluir datos de cursos asociados en la serialización de intentos
- feat(frontend): agregar selectores de filtro por curso y por reto en panel de envíos
- feat(frontend): agregar ordenamiento por fecha, estudiante, reto y puntos con dirección asc/desc
- feat(frontend): mostrar contador de resultados filtrados vs total
- refactor(frontend): actualizar firma de `pendingSubmissions` para aceptar múltiples parámetros de consulta
- feat(types): extender tipo `Attempt.challenge` con campo opcional `courses`
- feat(vite): agregar proxy para rutas `/health` y `/version` en servidor de desarrollo

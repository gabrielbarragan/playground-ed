# Changelog

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

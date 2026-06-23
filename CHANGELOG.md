# Changelog

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

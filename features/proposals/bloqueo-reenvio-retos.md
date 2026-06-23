# Bloqueo de Reenvío de Retos Resueltos o Pendientes

## Problema

Actualmente un estudiante puede seguir enviando soluciones a un reto que ya aprobó o que tiene un envío pendiente de revisión. Esto genera envíos innecesarios en la cola de revisión del docente y permite acumular intentos que no deberían existir.

## Estado Actual

### Backend

- `submit_challenge()` (`process.py:349-452`) no tiene ningún guard que impida reenviar:
  - Aunque calcula `already_passed` (línea 417), solo lo usa para decidir si acredita puntos, no para bloquear el envío.
  - No verifica si ya existe un intento con `review_status="pending"` para ese usuario/reto.
  - El `attempt_number` se incrementa sin límite.

- `AttemptQueryset` tiene `user_already_passed()` (`querysets.py:48-49`) pero no tiene un método equivalente para verificar envíos pendientes de revisión.

### Frontend

- El botón "Enviar" (`PlaygroundView.vue:151-158`) solo se deshabilita durante el envío en curso (`submitting`), sin considerar el estado del reto.
- El store (`useChallengesStore.ts`) no expone ningún computed que indique si el reto activo ya está resuelto o pendiente.
- El panel de retos (`ChallengesPanel.vue`) sí muestra visualmente el estado (`✓` / `⏳` / `○`) pero no impide seleccionar ni enviar.

## Cambios Propuestos

### Backend

1. **Agregar validación en `submit_challenge()`** (`process.py`):
   - Si el usuario ya aprobó el reto (`user_already_passed`) → `raise ValueError("Ya completaste este reto")`.
   - Si el usuario tiene un intento pendiente de revisión para ese reto → `raise ValueError("Ya tenés un envío pendiente de revisión para este reto")`.
   - Estas validaciones van antes de la ejecución de test cases para evitar consumo de recursos innecesario.

2. **Agregar método `has_pending_review()` en `AttemptQueryset`** (`querysets.py`):
   - `def has_pending_review(self, user, challenge) -> bool` — retorna `True` si existe un attempt con `review_status="pending"` para ese par usuario/reto.

### Frontend

1. **Deshabilitar botón "Enviar"** (`PlaygroundView.vue`):
   - Cuando el reto activo tiene status `passed` o `pending_review` en el progress del store.
   - Cambiar el texto del botón: "Resuelto ✓" / "En revisión ⏳" según corresponda.

2. **Exponer computed en el store** (`useChallengesStore.ts`):
   - `canSubmit`: `true` solo si hay un reto activo y su status es `unsolved`.

3. **Feedback visual en `ChallengeDescription.vue`**:
   - Si el reto ya fue aprobado: mostrar mensaje de confirmación y ocultar/deshabilitar la acción de envío.
   - Si tiene envío pendiente: mostrar estado "pendiente de revisión" con indicación de que no puede reenviar hasta que sea revisado.

## Archivos a Modificar

| Archivo | Cambio |
|---|---|
| `app/api/challenges/process.py` | Agregar guards al inicio de `submit_challenge()` |
| `app/api/challenges/querysets.py` | Agregar `has_pending_review(user, challenge)` |
| `frontend/src/stores/useChallengesStore.ts` | Agregar computed `canSubmit` |
| `frontend/src/features/playground/PlaygroundView.vue` | Condicionar botón "Enviar" con `canSubmit` |
| `frontend/src/features/playground/components/ChallengeDescription.vue` | Mensaje de estado cuando no se puede enviar |

## Casos Borde

- **Reto rechazado**: si el docente rechaza un envío, el status vuelve a `unsolved` y el estudiante puede reenviar. Esto ya funciona porque `review_status` pasa a `"rejected"` y `passed` sigue en `False`.
- **Reto sin revisión manual**: el bloqueo aplica solo si `passed=True` (ya resuelto). No se genera estado `pending`.
- **Docente resetea intento**: si a futuro se implementa un reset de intentos, los guards se basan en estado actual de la DB, así que se adaptan automáticamente.

## Tasks

- [x] **BL-1**: Agregar método `has_pending_review(user, challenge)` en `AttemptQueryset` (`querysets.py`) — retorna `True` si existe un attempt con `review_status="pending"` para ese par usuario/reto
- [x] **BL-2**: Agregar guard en `submit_challenge()` (`process.py`) que rechace el envío si `user_already_passed()` es `True` — `raise ValueError("Ya completaste este reto")`
- [x] **BL-3**: Agregar guard en `submit_challenge()` (`process.py`) que rechace el envío si `has_pending_review()` es `True` — `raise ValueError("Ya tenés un envío pendiente de revisión para este reto")`
- [x] **BL-4**: Verificar que ambos guards se ejecutan antes de la validación AST y ejecución de test cases
- [x] **BL-5**: Agregar computed `canSubmit` en `useChallengesStore.ts` — `true` solo si hay reto activo con status `unsolved`
- [x] **BL-6**: Condicionar botón "Enviar" en `PlaygroundView.vue` con `canSubmit`; cambiar texto a "Resuelto ✓" si `passed` o "En revisión ⏳" si `pending_review`
- [x] **BL-7**: Agregar mensaje de estado en `ChallengeDescription.vue` cuando el reto ya fue aprobado o está pendiente de revisión
- [x] **BL-8**: Verificar que el botón vuelve a habilitarse cuando el docente rechaza un envío y el estudiante recarga la vista
- [x] **BL-9**: Verificar que el backend retorna HTTP 400 con mensaje descriptivo al intentar enviar un reto ya resuelto o pendiente

## Requerimientos (Gherkin)

```gherkin
Feature: Bloqueo de reenvío de retos resueltos o pendientes
  Como plataforma educativa
  Quiero impedir que los estudiantes reenvíen un reto ya aprobado o con revisión pendiente
  Para evitar envíos innecesarios y mantener limpia la cola de revisión del docente

  Background:
    Given el estudiante está autenticado
    And existe un reto activo asignado al curso del estudiante

  # ── Bloqueo por reto ya aprobado ──────────────────────────────

  Scenario: Estudiante no puede enviar un reto que ya aprobó (backend)
    Given el estudiante ya aprobó el reto
    When envía una solución al mismo reto vía POST /api/v1/challenges/{id}/submit
    Then el backend responde con HTTP 400
    And el mensaje de error es "Ya completaste este reto"
    And no se crea un nuevo intento en la base de datos

  Scenario: Botón de envío muestra "Resuelto" para reto aprobado (frontend)
    Given el estudiante ya aprobó el reto
    When abre el reto en el playground
    Then el botón de envío muestra el texto "Resuelto ✓"
    And el botón está deshabilitado
    And no puede hacer click para enviar

  Scenario: Descripción del reto muestra confirmación de aprobación
    Given el estudiante ya aprobó el reto
    When abre el reto en el playground
    Then el panel de descripción muestra un mensaje indicando que el reto ya fue completado

  # ── Bloqueo por envío pendiente de revisión ───────────────────

  Scenario: Estudiante no puede enviar un reto con revisión pendiente (backend)
    Given el estudiante tiene un envío pendiente de revisión para el reto
    When envía una nueva solución al mismo reto vía POST /api/v1/challenges/{id}/submit
    Then el backend responde con HTTP 400
    And el mensaje de error es "Ya tenés un envío pendiente de revisión para este reto"
    And no se crea un nuevo intento en la base de datos

  Scenario: Botón de envío muestra "En revisión" para reto pendiente (frontend)
    Given el estudiante tiene un envío pendiente de revisión para el reto
    When abre el reto en el playground
    Then el botón de envío muestra el texto "En revisión ⏳"
    And el botón está deshabilitado

  Scenario: Descripción del reto muestra estado pendiente
    Given el estudiante tiene un envío pendiente de revisión para el reto
    When abre el reto en el playground
    Then el panel de descripción muestra un mensaje indicando que el envío está pendiente de revisión

  # ── Desbloqueo tras rechazo ───────────────────────────────────

  Scenario: Estudiante puede reenviar después de un rechazo
    Given el estudiante tenía un envío pendiente de revisión para el reto
    And el docente rechazó el envío
    When el estudiante recarga la vista del playground
    Then el botón de envío muestra "Enviar" y está habilitado
    And el estudiante puede enviar una nueva solución

  Scenario: Backend acepta reenvío después de rechazo
    Given el estudiante tenía un envío pendiente de revisión para el reto
    And el docente rechazó el envío con feedback "Revisar el uso de funciones"
    When el estudiante envía una nueva solución al reto vía POST
    Then el backend acepta el envío
    And se crea un nuevo intento con attempt_number incrementado

  # ── Retos sin revisión manual ─────────────────────────────────

  Scenario: Reto auto-evaluado permite reintentos mientras no pase
    Given el reto tiene test cases y requires_review es false
    And el estudiante envió una solución que no pasó los tests
    When envía una nueva solución
    Then el backend acepta el envío
    And se evalúa contra los test cases normalmente

  Scenario: Reto auto-evaluado bloquea envíos después de aprobar
    Given el reto tiene test cases y requires_review es false
    And el estudiante ya aprobó el reto (pasó todos los tests)
    When envía una nueva solución
    Then el backend responde con HTTP 400
    And el mensaje de error es "Ya completaste este reto"

  # ── Validación de orden de guards ─────────────────────────────

  Scenario: Guards se ejecutan antes de la ejecución de test cases
    Given el estudiante ya aprobó el reto
    When envía una nueva solución con código válido
    Then el backend rechaza el envío inmediatamente
    And no se ejecuta el código contra los test cases del sandbox

  Scenario: Guards se ejecutan antes de la validación AST
    Given el estudiante ya aprobó el reto
    When envía una nueva solución (incluso con código inválido para AST)
    Then el backend rechaza el envío con "Ya completaste este reto"
    And no se realiza la validación AST

  # ── Consistencia del estado ───────────────────────────────────

  Scenario: Progress refleja correctamente el estado tras bloqueo
    Given el estudiante ya aprobó el reto
    When consulta su progreso vía GET /api/v1/challenges/my-progress
    Then el reto aparece con status "passed"
    And el panel de retos muestra el ícono "✓" junto al reto
```

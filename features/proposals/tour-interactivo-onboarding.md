# Tour Interactivo de Onboarding

## Problema

Los usuarios nuevos (estudiantes y docentes) llegan a la plataforma sin una guía sobre cómo usar las funcionalidades. No hay ningún flujo de bienvenida, lo que puede resultar en:

- Estudiantes que no descubren que pueden guardar snippets, resolver retos, ver logros o consultar su dashboard.
- Docentes que no saben dónde revisar envíos, crear retos, gestionar estudiantes o ver analíticas.
- Funcionalidades que pasan desapercibidas porque no hay un recorrido inicial que las muestre.

## Objetivo

Implementar un tour interactivo paso a paso usando `driver.js` que resalte las secciones clave de la interfaz la primera vez que un usuario ingresa. El tour se diferencia por rol:

- **Estudiante**: tour en el Playground (`/`) con pasos por editor, terminal, snippets, retos, logros, y links a dashboard, evaluaciones y perfil.
- **Estudiante (Dashboard)**: tour en el Dashboard (`/dashboard`) con pasos por estadísticas, mapa de actividad, ranking y el botón de perfil (sidebar con cambio de correo, cambio de curso y repetir tour).
- **Docente**: tour en el Panel Admin (`/admin`) con pasos por tabs de usuarios, cursos, retos, revisiones, solicitudes, evaluaciones, logros y analítica.

El tour se activa automáticamente en el primer login y queda disponible para repetirlo desde el perfil o un botón de ayuda.

## Estado Actual

- No existe ningún sistema de onboarding, tooltips ni tours en la plataforma.
- `driver.js` no está instalado como dependencia.
- El Playground tiene elementos con clases CSS bien definidas que pueden usarse como selectores para los pasos del tour.
- El Panel Admin tiene tabs con IDs/clases identificables.
- No se persiste en backend si el usuario ya completó el tour. Se puede usar `localStorage` inicialmente.

## Cambios Propuestos

### Dependencia

Instalar `driver.js` (v1.x, ~5KB gzip):
```bash
cd frontend && npm install driver.js
```

### Composable `useTour`

Crear un composable reutilizable `frontend/src/composables/useTour.ts` que encapsule:

- Inicialización de `driver.js` con tema custom (colores Catppuccin Mocha del proyecto).
- Método `startTour(steps)` que recibe un array de pasos.
- Lógica de "primer login" basada en `localStorage` (key `tour_completed_<role>`).
- Método `resetTour()` para permitir repetir el tour.

### Tour del Estudiante

Se activa en `PlaygroundView.vue` al montar si es el primer login del estudiante.

**Pasos del tour:**

| # | Elemento | Título | Descripción |
|---|---|---|---|
| 1 | `.playground-header` | Bienvenido al Playground | Este es tu espacio para escribir y ejecutar código Python. Acá vas a practicar, resolver retos y guardar tus programas. |
| 2 | `.pane` (editor) | Editor de código | Escribí tu código Python acá. Usa `Ctrl+Enter` para ejecutar. El editor tiene autocompletado y resaltado de sintaxis. |
| 3 | `.btn-run` | Ejecutar código | Presioná este botón (o `Ctrl+Enter`) para ejecutar tu programa. Si el código tiene errores, los vas a ver en la terminal. |
| 4 | `.pane--right` | Terminal | Acá aparece la salida de tu programa: resultados, errores y también podés ingresar datos cuando el código pide input. |
| 5 | `.btn-snippets` | Mis Snippets | Guardá fragmentos de código para reutilizarlos después. Podés guardar, cargar y organizar tus programas. |
| 6 | `.btn-challenges` | Retos | Resolvé desafíos de programación asignados por tu docente. Cada reto tiene una descripción, ejemplos y casos de prueba. |
| 7 | `.btn-submit` (si visible) o paso informativo | Enviar solución | Cuando tengas un reto activo, usá este botón para enviar tu solución. Se evaluará automáticamente o quedará pendiente de revisión. |
| 8 | Link `Dashboard` en header | Dashboard | Visitá tu dashboard para ver tu actividad, racha de días, puntos, ranking del curso y logros desbloqueados. |
| 9 | Link `Evaluaciones` en header | Evaluaciones | Completá evaluaciones (quizzes) asignadas por tu docente. Cada una tiene preguntas y un puntaje mínimo para aprobar. |
| 10 | `.badge-btn` | Tu insignia | Elegí un emoji como insignia personal. Se muestra junto a tu nombre en el ranking. |

### Tour del Dashboard (Estudiante)

Se activa en `DashboardView.vue` al montar si es la primera vez que el estudiante entra al Dashboard (solo para no-admins).

**Pasos del tour:**

| # | Elemento | Título | Descripción |
|---|---|---|---|
| 1 | `.dash-header` | Tu Dashboard | Acá podés ver toda tu actividad: estadísticas, racha de días, ranking del curso y logros desbloqueados. |
| 2 | `.stats-row` | Estadísticas | Resumen rápido de tus días seguidos de actividad, ejecuciones en los últimos 15 días, puntos totales y líneas de código escritas. |
| 3 | `[data-tour="section-activity"]` | Actividad reciente | El mapa de calor muestra cuántas ejecuciones hiciste cada día. Pasá el mouse sobre cada celda para ver el detalle del día. |
| 4 | `[data-tour="section-ranking"]` | Ranking del curso | Posición de todos los estudiantes de tu curso ordenados por puntos. Tu fila aparece resaltada. |
| 5 | `.profile-toggle` | Mi Perfil | Abrí el sidebar de perfil para ver tu información de cuenta, cambiar tu correo electrónico, solicitar un cambio de curso o repetir el tour de la plataforma. |

### Tour del Docente

Se activa en `AdminView.vue` al montar si es el primer login del docente en el panel admin.

**Pasos del tour:**

| # | Elemento | Título | Descripción |
|---|---|---|---|
| 1 | `.admin-header` | Panel de Administración | Desde acá gestionás toda la actividad de tus cursos: estudiantes, retos, evaluaciones y más. |
| 2 | Tab `Usuarios` | Usuarios | Listado de todos los estudiantes de tus cursos. Podés ver su perfil, puntos, actividad reciente y gestionar su estado. |
| 3 | `.stats-row` | Estadísticas rápidas | Resumen de usuarios activos, inactivos, ejecuciones de la semana y actividad reciente de tus cursos. |
| 4 | `.courses-grid` | Filtro por curso | Hacé click en un curso para filtrar el listado de usuarios. Click de nuevo para ver todos. |
| 5 | `.cell-name--link` (primer usuario) | Perfil del estudiante | Hacé click en el nombre de un estudiante para ver su perfil completo: retos, quizzes, snippets, logros y actividad. |
| 6 | Tab `Cursos` | Cursos | Creá y gestioná cursos. Cada curso agrupa estudiantes y se asocia a retos y evaluaciones. |
| 7 | Tab `Retos` | Retos | Creá desafíos de programación con casos de prueba. Podés asignarlos a uno o más cursos, con revisión manual o automática. |
| 8 | Tab `Revisiones` | Revisiones | Revisá los envíos de estudiantes que requieren aprobación manual. Podés aprobar, rechazar y dejar feedback. |
| 9 | Tab `Solicitudes` | Solicitudes de cambio | Acá aparecen las solicitudes de estudiantes que quieren cambiarse de curso. Podés aprobar o rechazar cada una. |
| 10 | Tab `Evaluaciones` | Evaluaciones | Creá quizzes con preguntas de opción múltiple. Configurá puntaje, banco de preguntas aleatorias y veé resultados. |
| 11 | Tab `Logros` | Logros del Sandbox | Configurá logros que se desbloquean automáticamente cuando un estudiante usa conceptos avanzados (bucles, clases, lambda, etc). |
| 12 | Tab `Analítica` | Analítica | Visualizaciones de actividad, distribución de puntos y tendencias de uso de tus cursos. |

### Persistencia del estado del tour

- `localStorage` con key `tour_completed_student`, `tour_completed_dashboard` y `tour_completed_admin`.
- Al completar o cerrar el tour → se marca como completado.
- Se puede resetear desde el perfil del usuario.

### Botón para repetir el tour

- En el sidebar de perfil del Dashboard (`DashboardView.vue`): botones "Tour del Playground", "Tour del Dashboard" (solo estudiantes) y "Tour del Panel Admin" (solo admins).
- "Tour del Dashboard" resetea la key y relanza el tour en la misma vista sin navegar.
- Si el usuario es admin: agregar también "Repetir tour del Panel Admin" que limpia la key y navega a `/admin`.

### Tema visual

Los popover de `driver.js` se customizarán con los colores del proyecto (Catppuccin Mocha):

```css
.driver-popover {
  background: #181825;
  border: 1px solid #313244;
  color: #cdd6f4;
}
.driver-popover .driver-popover-title {
  color: #cba6f7;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
}
.driver-popover .driver-popover-description {
  color: #a6adc8;
}
.driver-popover .driver-popover-next-btn {
  background: #cba6f7;
  color: #1e1e2e;
}
.driver-popover .driver-popover-prev-btn {
  background: #313244;
  color: #cdd6f4;
}
.driver-popover .driver-popover-close-btn {
  color: #6c7086;
}
```

## Archivos a Crear/Modificar

### Nuevos archivos

| Archivo | Descripción |
|---|---|
| `frontend/src/composables/useTour.ts` | Composable con inicialización de driver.js, lógica de primer login, start/reset |
| `frontend/src/tours/studentTour.ts` | Definición de pasos del tour del estudiante (Playground) |
| `frontend/src/tours/dashboardTour.ts` | Definición de pasos del tour del Dashboard (estudiante) |
| `frontend/src/tours/adminTour.ts` | Definición de pasos del tour del docente |
| `frontend/src/tours/tourTheme.css` | Estilos custom de driver.js con colores Catppuccin Mocha |

### Archivos a modificar

| Archivo | Cambio |
|---|---|
| `frontend/package.json` | Agregar `driver.js` como dependencia |
| `frontend/src/features/playground/PlaygroundView.vue` | Importar composable, llamar tour en `onMounted` si es primer login |
| `frontend/src/features/dashboard/DashboardView.vue` | Importar composable, llamar tour dashboard en `onMounted` si es primer login; botones de repetir tour en sidebar de perfil; `data-tour` en secciones |
| `frontend/src/features/admin/AdminView.vue` | Importar composable, llamar tour en `onMounted` si es primer login del admin |
| `frontend/src/features/profile/ProfileView.vue` | Agregar botón "Repetir tour" que resetea localStorage y navega |
| `frontend/src/main.ts` | Importar `tourTheme.css` globalmente |

## Tasks

### Setup

- [x] **T-1**: Instalar `driver.js` — `cd frontend && npm install driver.js`
- [x] **T-2**: Crear `frontend/src/tours/tourTheme.css` con estilos custom Catppuccin Mocha para los popovers de driver.js
- [x] **T-3**: Importar `tourTheme.css` en `main.ts`

### Composable

- [x] **T-4**: Crear `frontend/src/composables/useTour.ts` con:
  - `shouldShowTour(key: string): boolean` — consulta `localStorage`
  - `startTour(steps: DriveStep[], key: string): void` — inicia tour con driver.js y marca como completado al finalizar/cerrar
  - `resetTour(key: string): void` — limpia la key de localStorage

### Tour del estudiante

- [x] **T-5**: Crear `frontend/src/tours/studentTour.ts` con array de pasos (10 pasos: header, editor, ejecutar, terminal, snippets, retos, enviar, dashboard, evaluaciones, badge)
- [x] **T-6**: Integrar tour en `PlaygroundView.vue` — llamar `startTour()` en `onMounted` si `shouldShowTour('student')` es `true` y el usuario no es admin
- [x] **T-7**: Agregar atributos `data-tour` a elementos del PlaygroundView que no tengan selectores CSS estables (si es necesario)

### Tour del docente

- [x] **T-8**: Crear `frontend/src/tours/adminTour.ts` con array de pasos (12 pasos: header, usuarios, stats, filtro cursos, perfil estudiante, cursos, retos, revisiones, solicitudes, evaluaciones, logros, analítica)
- [x] **T-9**: Integrar tour en `AdminView.vue` — llamar `startTour()` en `onMounted` si `shouldShowTour('admin')` es `true`
- [x] **T-10**: Agregar atributos `data-tour` a tabs y secciones del AdminView que no tengan selectores estables (si es necesario)

### Repetir tour

- [x] **T-11**: Agregar sección "Tour de la plataforma" en sidebar de perfil del Dashboard con botones "Tour del Playground", "Tour del Dashboard" (estudiantes) y "Tour del Panel Admin" (admins)
- [x] **T-12**: Al click, resetear la key en localStorage y navegar/relanzar el tour correspondiente

### Tour del Dashboard

- [x] **T-13**: Crear `frontend/src/tours/dashboardTour.ts` con array de pasos (5 pasos: header, estadísticas, actividad, ranking, perfil)
- [x] **T-14**: Agregar atributos `data-tour="section-activity"` y `data-tour="section-ranking"` en `DashboardView.vue`
- [x] **T-15**: Integrar tour en `DashboardView.vue` — llamar `startTour()` en `onMounted` tras cargar datos si `shouldShowTour('dashboard')` es `true` y el usuario no es admin

### Validación

- [ ] **QA-1**: Verificar que el tour del estudiante se muestra automáticamente al primer login
- [ ] **QA-2**: Verificar que el tour del estudiante NO se muestra en logins posteriores
- [ ] **QA-3**: Verificar que el tour del docente se muestra al entrar por primera vez a `/admin`
- [ ] **QA-4**: Verificar que los botones "Repetir tour" en el sidebar de perfil resetean y relanzan el tour correspondiente
- [ ] **QA-5**: Verificar que los popovers tienen los colores correctos del tema Catppuccin Mocha
- [ ] **QA-6**: Verificar que el tour se adapta correctamente en pantallas móviles (responsive)
- [ ] **QA-7**: Verificar que cerrar el tour antes de terminar lo marca como completado (no se repite)
- [ ] **QA-8**: Verificar que el tour del Dashboard se muestra la primera vez que el estudiante entra a `/dashboard`
- [ ] **QA-9**: Verificar que el tour del Dashboard NO se muestra si el usuario es admin
- [ ] **QA-10**: Verificar que el botón "Tour del Dashboard" en el sidebar de perfil relanza el tour sin navegar

## Requerimientos (Gherkin)

```gherkin
Feature: Tour interactivo de onboarding
  Como plataforma educativa
  Quiero guiar a los usuarios nuevos con un tour paso a paso
  Para que descubran las funcionalidades principales sin ayuda externa

  Background:
    Given el usuario está autenticado

  # ── Tour del estudiante ─────────────────────────────────

  Scenario: Tour se muestra automáticamente al primer login del estudiante
    Given es la primera vez que el estudiante inicia sesión
    When se carga el Playground
    Then aparece un overlay con el primer paso del tour
    And el paso resalta el header del Playground con título "Bienvenido al Playground"

  Scenario: Tour avanza paso a paso
    Given el tour del estudiante está activo en el paso 1
    When el estudiante hace click en "Siguiente"
    Then el tour avanza al paso 2 resaltando el editor de código
    And muestra el título "Editor de código"

  Scenario: Tour se puede cerrar en cualquier momento
    Given el tour del estudiante está activo
    When el estudiante hace click en "X" (cerrar)
    Then el tour se cierra
    And se marca como completado en localStorage

  Scenario: Tour no se repite en logins posteriores
    Given el estudiante ya completó el tour
    When vuelve a cargar el Playground
    Then el tour NO se muestra automáticamente

  Scenario: Tour se puede repetir desde el perfil
    Given el estudiante ya completó el tour
    When va a su perfil y hace click en "Repetir tour del Playground"
    Then se redirige al Playground
    And el tour comienza desde el paso 1

  # ── Tour del Dashboard ──────────────────────────────────

  Scenario: Tour del Dashboard se muestra la primera vez que el estudiante lo visita
    Given es la primera vez que el estudiante entra al Dashboard
    When se carga la vista /dashboard
    Then aparece un overlay con el primer paso del tour del Dashboard
    And el paso resalta el header con título "Tu Dashboard"

  Scenario: Tour del Dashboard recorre estadísticas, actividad, ranking y perfil
    Given el tour del Dashboard está activo
    When el estudiante avanza por todos los pasos
    Then los pasos resaltan en orden: header, stats-row, section-activity, section-ranking, profile-toggle

  Scenario: Tour del Dashboard no se muestra si el usuario es admin
    Given el usuario autenticado es docente (admin)
    When entra al Dashboard
    Then el tour del Dashboard NO se activa

  Scenario: Estudiante puede repetir el tour del Dashboard desde el sidebar de perfil
    Given el estudiante ya completó el tour del Dashboard
    When abre el sidebar de perfil y hace click en "Tour del Dashboard"
    Then el tour se relanza desde el paso 1 sin navegar a otra ruta

  # ── Tour del docente ────────────────────────────────────

  Scenario: Tour del docente se muestra al entrar por primera vez al panel admin
    Given es la primera vez que el docente entra a /admin
    When se carga el Panel Admin
    Then aparece un overlay con el primer paso del tour del docente
    And el paso resalta el header del admin con título "Panel de Administración"

  Scenario: Tour del docente recorre los tabs principales
    Given el tour del docente está activo
    When el docente avanza por todos los pasos
    Then cada tab principal se resalta en orden: Usuarios, Cursos, Retos, Revisiones, Solicitudes, Evaluaciones, Logros, Analítica

  Scenario: Docente puede repetir el tour del admin desde su perfil
    Given el docente ya completó el tour del admin
    When va a su perfil y hace click en "Repetir tour del Panel Admin"
    Then se redirige a /admin
    And el tour comienza desde el paso 1

  # ── Tema visual ─────────────────────────────────────────

  Scenario: Los popovers del tour usan el tema del proyecto
    Given el tour está activo
    Then los popovers tienen fondo #181825
    And los títulos son color #cba6f7
    And los botones "Siguiente" son color #cba6f7 con texto #1e1e2e
```

## Notas

- **driver.js v1.x** (~5KB gzip) se elige sobre Shepherd.js (~25KB) por su tamaño mínimo y API simple. No necesita dependencias externas.
- **localStorage vs backend**: inicialmente el estado del tour se guarda en localStorage. Si a futuro se necesita sincronizar entre dispositivos, se puede agregar un campo `tour_completed` al modelo User.
- **Timing del tour**: el tour del estudiante debe esperar a que el editor Monaco termine de renderizar (`nextTick` + pequeño delay) antes de iniciar.
- **No bloquear la UI**: si el usuario cierra el tour, no debe volver a aparecer hasta que lo resetee explícitamente.
- **Responsividad**: driver.js se adapta automáticamente al tamaño del viewport, pero los pasos que apuntan a elementos ocultos en mobile deben condicionarse.
- **El tour del docente funciona con tabs**: algunos pasos apuntan a tabs que no están visibles simultáneamente. Para estos, el popover se posiciona sobre el botón del tab en la barra de navegación, no sobre el contenido del tab.

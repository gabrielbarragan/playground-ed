import type { DriveStep } from 'driver.js'

export const adminTourSteps: DriveStep[] = [
  {
    element: '.admin-header',
    popover: {
      title: 'Panel de Administración',
      description: 'Desde acá gestionas toda la actividad de tus cursos: estudiantes, retos, evaluaciones y más.',
      side: 'bottom',
      align: 'center',
    },
  },
  {
    element: '[data-tour="tab-users"]',
    popover: {
      title: 'Usuarios',
      description: 'Listado de todos los estudiantes de tus cursos. Puedes ver su perfil, puntos, actividad reciente y gestionar su estado.',
      side: 'bottom',
      align: 'start',
    },
  },
  {
    element: '.stats-row',
    popover: {
      title: 'Estadísticas rápidas',
      description: 'Resumen de usuarios activos, inactivos, ejecuciones de la semana y actividad reciente de tus cursos.',
      side: 'bottom',
      align: 'center',
    },
  },
  {
    element: '.courses-grid',
    popover: {
      title: 'Filtro por curso',
      description: 'Haces click en un curso para filtrar el listado de usuarios. Click de nuevo para ver todos.',
      side: 'bottom',
      align: 'center',
    },
  },
  {
    element: '[data-tour="tab-courses"]',
    popover: {
      title: 'Cursos',
      description: 'Crea y gestiona cursos. Cada curso agrupa estudiantes y se asocia a retos y evaluaciones.',
      side: 'bottom',
      align: 'start',
    },
  },
  {
    element: '[data-tour="tab-challenges"]',
    popover: {
      title: 'Retos',
      description: 'Crea desafíos de programación con casos de prueba. Puedes asignarlos a uno o más cursos, con revisión manual o automática.',
      side: 'bottom',
      align: 'start',
    },
  },
  {
    element: '[data-tour="tab-submissions"]',
    popover: {
      title: 'Revisiones',
      description: 'Revisa los envíos de estudiantes que requieren aprobación manual. Puedes aprobar, rechazar y dejar feedback.',
      side: 'bottom',
      align: 'start',
    },
  },
  {
    element: '[data-tour="tab-course-requests"]',
    popover: {
      title: 'Solicitudes de cambio',
      description: 'Acá aparecen las solicitudes de estudiantes que quieren cambiarse de curso. Podés aprobar o rechazar cada una.',
      side: 'bottom',
      align: 'start',
    },
  },
  {
    element: '[data-tour="tab-quizzes"]',
    popover: {
      title: 'Evaluaciones',
      description: 'Crea quizzes con preguntas de opción múltiple. Configura puntaje, banco de preguntas aleatorias y ve resultados.',
      side: 'bottom',
      align: 'start',
    },
  },
  {
    element: '[data-tour="tab-achievements"]',
    popover: {
      title: 'Logros del Sandbox',
      description: 'Configura logros que se desbloquean automáticamente cuando un estudiante usa conceptos avanzados como bucles, clases o lambda.',
      side: 'bottom',
      align: 'start',
    },
  },
  {
    element: '[data-tour="tab-analytics"]',
    popover: {
      title: 'Analítica',
      description: 'Visualizaciones de actividad, distribución de puntos y tendencias de uso de tus cursos.',
      side: 'bottom',
      align: 'start',
    },
  },
]

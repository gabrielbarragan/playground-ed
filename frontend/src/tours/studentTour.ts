import type { DriveStep } from 'driver.js'

export const studentTourSteps: DriveStep[] = [
  {
    element: '.playground-header',
    popover: {
      title: 'Bienvenido al Playground',
      description: 'Este es tu espacio para escribir y ejecutar código Python. Acá vas a practicar, resolver retos y guardar tus programas.',
      side: 'bottom',
      align: 'center',
    },
  },
  {
    element: '.pane:first-child',
    popover: {
      title: 'Editor de código',
      description: 'Escribe tu código Python acá. Tiene autocompletado y resaltado de sintaxis para ayudarte.',
      side: 'right',
      align: 'center',
    },
  },
  {
    element: '.btn-run',
    popover: {
      title: 'Ejecutar código',
      description: 'Presiona este botón o usa Ctrl+Enter para ejecutar tu programa.',
      side: 'bottom',
      align: 'start',
    },
  },
  {
    element: '.pane--right',
    popover: {
      title: 'Terminal',
      description: 'Acá aparece la salida de tu programa: resultados, errores y también puedes ingresar datos cuando el código pide input.',
      side: 'left',
      align: 'center',
    },
  },
  {
    element: '.btn-snippets',
    popover: {
      title: 'Mis Snippets',
      description: 'Guarda fragmentos de código para reutilizarlos después. Puedes guardar, cargar y organizar tus programas.',
      side: 'bottom',
      align: 'center',
    },
  },
  {
    element: '.btn-challenges',
    popover: {
      title: 'Retos',
      description: 'Resuelve desafíos de programación asignados por tu docente. Cada reto tiene una descripción, ejemplos y casos de prueba.',
      side: 'bottom',
      align: 'center',
    },
  },
  {
    element: '[data-tour="link-dashboard"]',
    popover: {
      title: 'Dashboard',
      description: 'Visita tu dashboard para ver tu actividad, racha de días, puntos, ranking del curso y logros desbloqueados.',
      side: 'bottom',
      align: 'center',
    },
  },
  {
    element: '[data-tour="link-quizzes"]',
    popover: {
      title: 'Evaluaciones',
      description: 'Completa evaluaciones asignadas por tu docente. Cada una tiene preguntas y un puntaje mínimo para aprobar.',
      side: 'bottom',
      align: 'center',
    },
  },
  {
    element: '.badge-btn',
    popover: {
      title: 'Tu insignia',
      description: 'Elige un emoji como insignia personal. Se muestra junto a tu nombre en el ranking del curso.',
      side: 'bottom',
      align: 'end',
    },
  },
]

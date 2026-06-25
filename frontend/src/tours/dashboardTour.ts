import type { DriveStep } from 'driver.js'

export const dashboardTourSteps: DriveStep[] = [
  {
    element: '.dash-header',
    popover: {
      title: 'Tu Dashboard',
      description: 'Acá podés ver toda tu actividad: estadísticas, racha de días, ranking del curso y logros desbloqueados.',
      side: 'bottom',
      align: 'center',
    },
  },
  {
    element: '.stats-row',
    popover: {
      title: 'Estadísticas',
      description: 'Resumen rápido de tus días seguidos de actividad, ejecuciones en los últimos 15 días, puntos totales y líneas de código escritas.',
      side: 'bottom',
      align: 'center',
    },
  },
  {
    element: '[data-tour="section-activity"]',
    popover: {
      title: 'Actividad reciente',
      description: 'El mapa de calor muestra cuántas ejecuciones hiciste cada día. Pasá el mouse sobre cada celda para ver el detalle del día.',
      side: 'bottom',
      align: 'center',
    },
  },
  {
    element: '[data-tour="section-ranking"]',
    popover: {
      title: 'Ranking del curso',
      description: 'Posición de todos los estudiantes de tu curso ordenados por puntos. Tu fila aparece resaltada.',
      side: 'top',
      align: 'center',
    },
  },
  {
    element: '.profile-toggle',
    popover: {
      title: 'Mi Perfil',
      description: 'Abrí el sidebar de perfil para ver tu información de cuenta, cambiar tu correo electrónico, solicitar un cambio de curso o repetir el tour de la plataforma.',
      side: 'bottom',
      align: 'end',
    },
  },
]

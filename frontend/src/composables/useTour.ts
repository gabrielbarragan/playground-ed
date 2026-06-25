import { driver, type DriveStep } from 'driver.js'
import 'driver.js/dist/driver.css'

const TOUR_PREFIX = 'tour_completed_'

export function useTour() {
  function shouldShowTour(key: string): boolean {
    return !localStorage.getItem(`${TOUR_PREFIX}${key}`)
  }

  function startTour(steps: DriveStep[], key: string) {
    const tour = driver({
      showProgress: true,
      showButtons: ['next', 'previous', 'close'],
      nextBtnText: 'Siguiente',
      prevBtnText: 'Anterior',
      doneBtnText: 'Finalizar',
      progressText: '{{current}} de {{total}}',
      steps,
      onDestroyed: () => {
        localStorage.setItem(`${TOUR_PREFIX}${key}`, '1')
      },
    })
    tour.drive()
  }

  function resetTour(key: string) {
    localStorage.removeItem(`${TOUR_PREFIX}${key}`)
  }

  return { shouldShowTour, startTour, resetTour }
}

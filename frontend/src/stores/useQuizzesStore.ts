import { defineStore } from 'pinia'
import { ref } from 'vue'
import { quizzesApi } from '@/api/quizzesApi'
import type { Quiz, QuizProgress, QuizAttempt } from '@/types/quizzes'

export const useQuizzesStore = defineStore('quizzes', () => {
  const quizzes = ref<QuizProgress[]>([])
  const activeQuiz = ref<Quiz | null>(null)
  const lastAttempt = ref<QuizAttempt | null>(null)
  const loading = ref(false)
  const submitting = ref(false)

  async function fetchQuizzes() {
    loading.value = true
    try {
      const res = await quizzesApi.list()
      quizzes.value = res.quizzes
    } finally {
      loading.value = false
    }
  }

  async function openQuiz(id: string): Promise<Quiz> {
    lastAttempt.value = null
    const quiz = await quizzesApi.get(id)
    activeQuiz.value = quiz
    return quiz
  }

  async function openResult(id: string): Promise<QuizAttempt> {
    const attempt = await quizzesApi.myResult(id)
    // Obtener el quiz si no está cargado (para mostrar datos del quiz junto al resultado)
    if (!activeQuiz.value || activeQuiz.value.id !== id) {
      const quiz = await quizzesApi.get(id)
      activeQuiz.value = quiz
    }
    lastAttempt.value = attempt
    return attempt
  }

  function closeQuiz() {
    activeQuiz.value = null
    lastAttempt.value = null
  }

  async function submit(answers: number[]): Promise<QuizAttempt> {
    if (!activeQuiz.value) throw new Error('No hay quiz activo')
    submitting.value = true
    try {
      const attempt = await quizzesApi.submit(activeQuiz.value.id, answers)
      lastAttempt.value = attempt
      // Actualizar estado en la lista
      const idx = quizzes.value.findIndex(q => q.id === activeQuiz.value!.id)
      if (idx >= 0) {
        quizzes.value[idx].status = attempt.passed ? 'passed' : 'completed'
      }
      return attempt
    } finally {
      submitting.value = false
    }
  }

  return {
    quizzes,
    activeQuiz,
    lastAttempt,
    loading,
    submitting,
    fetchQuizzes,
    openQuiz,
    openResult,
    closeQuiz,
    submit,
  }
})
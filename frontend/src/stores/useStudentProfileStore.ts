import { defineStore } from 'pinia'
import { ref } from 'vue'
import { studentProfileApi } from '@/api/studentProfileApi'

export const useStudentProfileStore = defineStore('studentProfile', () => {
  const userId = ref<string | null>(null)
  const summary = ref<any>(null)
  const challenges = ref<any>(null)
  const quizzes = ref<any>(null)
  const attempts = ref<any>(null)
  const snippets = ref<any>(null)
  const achievements = ref<any>(null)
  const pointsBreakdown = ref<any>(null)

  const loadingSummary = ref(false)
  const loadingChallenges = ref(false)
  const loadingQuizzes = ref(false)
  const loadingAttempts = ref(false)
  const loadingSnippets = ref(false)
  const loadingAchievements = ref(false)
  const loadingPoints = ref(false)

  function open(id: string) {
    if (userId.value === id) return
    userId.value = id
    summary.value = null
    challenges.value = null
    quizzes.value = null
    attempts.value = null
    snippets.value = null
    achievements.value = null
    pointsBreakdown.value = null
    loadSummary()
  }

  function close() {
    userId.value = null
  }

  async function loadSummary() {
    if (!userId.value) return
    loadingSummary.value = true
    try {
      summary.value = await studentProfileApi.getSummary(userId.value)
    } finally {
      loadingSummary.value = false
    }
  }

  async function loadChallenges() {
    if (!userId.value || challenges.value) return
    loadingChallenges.value = true
    try {
      challenges.value = await studentProfileApi.getChallenges(userId.value)
    } finally {
      loadingChallenges.value = false
    }
  }

  async function loadQuizzes() {
    if (!userId.value || quizzes.value) return
    loadingQuizzes.value = true
    try {
      quizzes.value = await studentProfileApi.getQuizzes(userId.value)
    } finally {
      loadingQuizzes.value = false
    }
  }

  async function loadAttempts() {
    if (!userId.value || attempts.value) return
    loadingAttempts.value = true
    try {
      attempts.value = await studentProfileApi.getAttempts(userId.value)
    } finally {
      loadingAttempts.value = false
    }
  }

  async function loadSnippets() {
    if (!userId.value || snippets.value) return
    loadingSnippets.value = true
    try {
      snippets.value = await studentProfileApi.getSnippets(userId.value)
    } finally {
      loadingSnippets.value = false
    }
  }

  async function loadAchievements() {
    if (!userId.value || achievements.value) return
    loadingAchievements.value = true
    try {
      achievements.value = await studentProfileApi.getAchievements(userId.value)
    } finally {
      loadingAchievements.value = false
    }
  }

  async function loadPointsBreakdown() {
    if (!userId.value || pointsBreakdown.value) return
    loadingPoints.value = true
    try {
      pointsBreakdown.value = await studentProfileApi.getPointsBreakdown(userId.value)
    } finally {
      loadingPoints.value = false
    }
  }

  return {
    userId,
    summary,
    challenges,
    quizzes,
    attempts,
    snippets,
    achievements,
    pointsBreakdown,
    loadingSummary,
    loadingChallenges,
    loadingQuizzes,
    loadingAttempts,
    loadingSnippets,
    loadingAchievements,
    loadingPoints,
    open,
    close,
    loadSummary,
    loadChallenges,
    loadQuizzes,
    loadAttempts,
    loadSnippets,
    loadAchievements,
    loadPointsBreakdown,
  }
})

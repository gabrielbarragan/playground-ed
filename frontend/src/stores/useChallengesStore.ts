import { defineStore } from 'pinia'
import { ref } from 'vue'
import { challengesApi } from '@/api/challengesApi'
import type { Challenge, ChallengeProgress, Attempt } from '@/types/challenges'

export const useChallengesStore = defineStore('challenges', () => {
  const progress = ref<ChallengeProgress[]>([])
  const activeChallenge = ref<Challenge | null>(null)
  const lastAttempt = ref<Attempt | null>(null)
  const submitting = ref(false)
  const loading = ref(false)

  async function fetchProgress() {
    loading.value = true
    try {
      const res = await challengesApi.myProgress()
      progress.value = res.challenges
    } finally {
      loading.value = false
    }
  }

  async function openChallenge(id: string) {
    lastAttempt.value = null
    const challenge = await challengesApi.get(id)
    activeChallenge.value = challenge
    return challenge
  }

  function closeChallenge() {
    activeChallenge.value = null
    lastAttempt.value = null
  }

  async function submit(code: string): Promise<Attempt> {
    if (!activeChallenge.value) throw new Error('No hay reto activo')
    submitting.value = true
    try {
      const attempt = await challengesApi.submit(activeChallenge.value.id, code)
      lastAttempt.value = attempt
      const idx = progress.value.findIndex(c => c.id === activeChallenge.value!.id)
      if (idx >= 0) {
        if (attempt.passed) progress.value[idx].status = 'passed'
        else if (attempt.review_status === 'pending') progress.value[idx].status = 'pending_review'
      }
      return attempt
    } finally {
      submitting.value = false
    }
  }

  return {
    progress,
    activeChallenge,
    lastAttempt,
    loading,
    submitting,
    fetchProgress,
    openChallenge,
    closeChallenge,
    submit,
  }
})
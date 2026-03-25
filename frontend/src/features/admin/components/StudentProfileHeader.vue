<template>
  <div class="sph">
    <div class="sph-top">
      <span class="sph-badge">{{ summary.user.badge }}</span>
      <div class="sph-info">
        <h2 class="sph-name">{{ summary.user.first_name }} {{ summary.user.last_name }}</h2>
        <div class="sph-meta">
          <span v-if="summary.user.course" class="course-chip">{{ summary.user.course.code }}</span>
          <span class="status-chip" :class="summary.user.is_active ? 'status--active' : 'status--inactive'">
            {{ summary.user.is_active ? 'Activo' : 'Inactivo' }}
          </span>
          <span class="sph-email">{{ summary.user.email }}</span>
        </div>
        <div class="sph-dates">
          <span>Desde {{ formatDate(summary.user.created_at) }}</span>
          <span class="sph-sep">·</span>
          <span>Último acceso: {{ summary.user.last_login ? formatDate(summary.user.last_login) : 'Nunca' }}</span>
        </div>
      </div>
    </div>

    <!-- Alerta de entregas pendientes de revisión -->
    <div v-if="summary.pending_review_count > 0" class="sph-review-alert">
      <span>{{ summary.pending_review_count }} entrega{{ summary.pending_review_count > 1 ? 's' : '' }} pendiente{{ summary.pending_review_count > 1 ? 's' : '' }} de revisión</span>
      <button class="review-link" @click="$emit('go-to-submissions')">Ver revisiones →</button>
    </div>

    <!-- Stats rápidos -->
    <div class="sph-stats">
      <div class="stat-card">
        <span class="stat-value">{{ summary.user.total_points }}</span>
        <span class="stat-label">pts totales</span>
      </div>
      <div class="stat-card stat-card--highlight">
        <span class="stat-value">+{{ summary.points_this_week }}</span>
        <span class="stat-label">pts esta semana</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{{ summary.challenges_solved }}<span class="stat-of">/{{ summary.challenges_total }}</span></span>
        <span class="stat-label">retos</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{{ summary.quizzes_passed }}<span class="stat-of">/{{ summary.quizzes_total }}</span></span>
        <span class="stat-label">quizzes ✓</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{{ summary.streak_days }}</span>
        <span class="stat-label">días seguidos</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{{ summary.snippets_count }}</span>
        <span class="stat-label">snippets</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{{ summary.achievements_count }}</span>
        <span class="stat-label">logros</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ summary: any }>()
defineEmits(['go-to-submissions'])

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('es-AR', {
    day: '2-digit', month: 'short', year: 'numeric',
  })
}
</script>

<style scoped>
.sph { display: flex; flex-direction: column; gap: 1rem; }

.sph-top { display: flex; align-items: flex-start; gap: 1rem; }

.sph-badge { font-size: 2.5rem; line-height: 1; }

.sph-info { display: flex; flex-direction: column; gap: 0.3rem; }

.sph-name { margin: 0; font-size: 1.2rem; font-weight: 600; color: #cdd6f4; }

.sph-meta { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }

.sph-email { font-size: 0.8rem; color: #6c7086; }

.sph-dates { font-size: 0.78rem; color: #6c7086; display: flex; gap: 0.4rem; }

.sph-sep { color: #45475a; }

.course-chip {
  font-size: 0.72rem; font-weight: 600; padding: 0.15rem 0.5rem;
  border-radius: 999px; background: #313244; color: #cba6f7;
}

.status-chip {
  font-size: 0.72rem; font-weight: 500; padding: 0.15rem 0.5rem;
  border-radius: 999px;
}
.status--active { background: rgba(166,227,161,0.15); color: #a6e3a1; }
.status--inactive { background: rgba(243,139,168,0.15); color: #f38ba8; }

.sph-review-alert {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.5rem 0.75rem; border-radius: 6px;
  background: rgba(249,226,175,0.1); border: 1px solid rgba(249,226,175,0.25);
  font-size: 0.82rem; color: #f9e2af;
}

.review-link {
  background: none; border: none; color: #cba6f7;
  font-size: 0.82rem; cursor: pointer; padding: 0;
}
.review-link:hover { text-decoration: underline; }

.sph-stats {
  display: flex; gap: 0.5rem; flex-wrap: wrap;
}

.stat-card {
  display: flex; flex-direction: column; align-items: center;
  padding: 0.6rem 0.8rem; border-radius: 8px;
  background: #181825; border: 1px solid #313244;
  min-width: 70px; gap: 0.2rem;
}

.stat-card--highlight {
  border-color: rgba(166,227,161,0.4);
  background: rgba(166,227,161,0.05);
}

.stat-value {
  font-size: 1.1rem; font-weight: 700; color: #cdd6f4;
}

.stat-of {
  font-size: 0.75rem; font-weight: 400; color: #6c7086;
}

.stat-label { font-size: 0.7rem; color: #6c7086; white-space: nowrap; }
</style>

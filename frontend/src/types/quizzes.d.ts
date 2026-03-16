export interface QuizOption {
  text: string
}

export interface QuizQuestion {
  index: number
  text: string
  code_block: string
  code_language: string
  options: QuizOption[]
  // correct_option_index NUNCA viene en la respuesta de estudiante pre-entrega
}

export interface QuizQuestionWithAnswer extends QuizQuestion {
  correct_option_index?: number  // Solo post-entrega si show_correct_answers=true
  explanation?: string
  is_correct?: boolean           // Del intento del usuario
  selected_option_index?: number // Respuesta elegida
}

export interface Quiz {
  id: string
  title: string
  description: string
  courses: { id: string; name: string; code: string }[]
  questions: QuizQuestion[]
  question_count: number
  passing_score: number
  points_on_complete: number
  points_on_pass: number
  show_correct_answers: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface QuizProgress {
  id: string
  title: string
  description: string
  question_count: number
  passing_score: number
  points_on_complete: number
  points_on_pass: number
  show_correct_answers: boolean
  status: 'pending' | 'completed' | 'passed'
  courses: { id: string; name: string; code: string }[]
}

export interface QuizAttempt {
  id: string
  quiz_id: string
  correct_count: number
  total_questions: number
  passed: boolean
  points_earned: number
  submitted_at: string
  questions?: QuizQuestionWithAnswer[] // Solo si show_correct_answers=true
}

export interface QuizStudentResult {
  id: string
  user: {
    id: string
    first_name: string
    last_name: string
    email: string
  }
  correct_count: number
  total_questions: number
  passed: boolean
  points_earned: number
  submitted_at: string
}
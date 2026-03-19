export interface TestCase {
  index: number
  input?: string
  expected_output?: string
  is_hidden: boolean
  description: string
}

export interface Challenge {
  id: string
  title: string
  description: string
  difficulty: 'easy' | 'medium' | 'hard'
  points: number
  courses: { id: string; name: string; code: string }[]
  starter_code: string
  example_input: string
  example_output: string
  requires_review: boolean
  required_functions: string[]
  tags: string[]
  test_cases: TestCase[]
  test_case_count: number
  has_auto_grading: boolean
  is_active: boolean
  optimal_lines_min: number | null
  optimal_lines_max: number | null
  lines_bonus_points: number
  created_at: string
  updated_at: string
}

export interface ChallengeProgress {
  id: string
  title: string
  difficulty: 'easy' | 'medium' | 'hard'
  points: number
  requires_review: boolean
  has_auto_grading: boolean
  status: 'passed' | 'pending_review' | 'unsolved'
  courses: { id: string; name: string; code: string }[]
}

export interface TestCaseResult {
  test_index: number
  passed: boolean
  actual_output: string
  error: string
}

export interface Attempt {
  id: string
  user: { id: string; first_name: string; last_name: string; email: string }
  challenge: { id: string; title: string; difficulty: string; points: number }
  code: string
  attempt_number: number
  passed: boolean
  points_earned: number
  bonus_points_earned: number
  effective_lines: number
  ast_validation_error: string
  review_status: 'pending' | 'approved' | 'rejected' | null
  review_feedback: string
  reviewer: { id: string; first_name: string; last_name: string } | null
  reviewed_at: string | null
  submitted_at: string
  results: TestCaseResult[]
}
export interface AuthUser {
  id: string
  first_name: string
  last_name: string
  email: string
  is_admin: boolean
  badge: string
  course: { id: string; name: string; code: string }
  total_points: number
}

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  first_name: string
  last_name: string
  email: string
  password: string
  course_id: string
}

export interface Course {
  id: string
  name: string
  code: string
  description: string
}
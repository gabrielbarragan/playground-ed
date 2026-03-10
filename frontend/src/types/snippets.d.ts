export interface Snippet {
  id: string
  title: string
  code: string
  language: string
  tags: string[]
  is_public: boolean
  created_at: string
  updated_at: string
}

export interface SaveSnippetPayload {
  title: string
  code: string
  language?: string
  tags?: string[]
}

export interface UpdateSnippetPayload {
  title: string
  code: string
  tags?: string[]
}
export interface Env {
  DB: D1Database;
  GROQ_API_KEY: string;
  GROQ_MODEL?: string;
  PROMPT_VERSION?: string;
  ALLOWED_ORIGIN?: string;
}

export interface AnswerRequestPayload {
  questionId: string;
  pdfId: string;
  pdfUrl: string;
  subjectSlug: string;
  subjectName?: string;
  semester: string;
  branch: string;
  questionNumber?: string;
  subquestion?: string;
  marks?: string;
  paperLabel?: string;
  questionText: string;
}

export interface QuestionAnswerRow {
  id: number;
  question_id: string;
  pdf_id: string;
  pdf_url: string;
  subject_slug: string;
  semester: string;
  branch: string;
  question_text: string;
  generated_answer: string | null;
  model_used: string | null;
  answer_hash: string | null;
  cache_hit_count: number;
  generate_button_clicks: number;
  worker_response_time_ms: number | null;
  prompt_version: string;
  generation_status: string;
  generation_error: string | null;
  created_at: string;
  updated_at: string;
  last_accessed_at: string;
}

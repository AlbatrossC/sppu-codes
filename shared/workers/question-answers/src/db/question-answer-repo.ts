import {
  STATUS_COMPLETE,
  STATUS_FAILED,
  STATUS_GENERATING
} from "../constants/config";
import type { AnswerRequestPayload, QuestionAnswerRow } from "../types/env";

export async function findByQuestionId(db: D1Database, questionId: string): Promise<QuestionAnswerRow | null> {
  const result = await db
    .prepare("SELECT * FROM question_answers WHERE question_id = ?1 LIMIT 1")
    .bind(questionId)
    .first<QuestionAnswerRow>();

  return result || null;
}

export async function markGenerating(
  db: D1Database,
  payload: AnswerRequestPayload,
  promptVersion: string
): Promise<void> {
  await db.prepare(
    `INSERT INTO question_answers (
      question_id, pdf_id, pdf_url, subject_slug, semester, branch, question_text,
      generate_button_clicks, prompt_version, generation_status, generation_error,
      created_at, updated_at, last_accessed_at
    ) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, 1, ?8, ?9, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    ON CONFLICT(question_id) DO UPDATE SET
      pdf_id = excluded.pdf_id,
      pdf_url = excluded.pdf_url,
      subject_slug = excluded.subject_slug,
      semester = excluded.semester,
      branch = excluded.branch,
      question_text = excluded.question_text,
      generate_button_clicks = question_answers.generate_button_clicks + 1,
      prompt_version = excluded.prompt_version,
      generation_status = ?10,
      generation_error = NULL,
      updated_at = CURRENT_TIMESTAMP,
      last_accessed_at = CURRENT_TIMESTAMP`
  )
    .bind(
      payload.questionId,
      payload.pdfId,
      payload.pdfUrl,
      payload.subjectSlug,
      payload.semester,
      payload.branch,
      payload.questionText,
      promptVersion,
      STATUS_GENERATING,
      STATUS_GENERATING
    )
    .run();
}

export async function recordCacheHit(db: D1Database, questionId: string): Promise<void> {
  await db.prepare(
    `UPDATE question_answers
      SET cache_hit_count = cache_hit_count + 1,
          generate_button_clicks = generate_button_clicks + 1,
          updated_at = CURRENT_TIMESTAMP,
          last_accessed_at = CURRENT_TIMESTAMP
      WHERE question_id = ?1`
  )
    .bind(questionId)
    .run();
}

export async function saveCompleted(
  db: D1Database,
  questionId: string,
  generatedAnswer: string,
  modelUsed: string,
  answerHash: string,
  workerResponseTimeMs: number
): Promise<void> {
  await db.prepare(
    `UPDATE question_answers
      SET generated_answer = ?2,
          model_used = ?3,
          answer_hash = ?4,
          worker_response_time_ms = ?5,
          generation_status = ?6,
          generation_error = NULL,
          updated_at = CURRENT_TIMESTAMP,
          last_accessed_at = CURRENT_TIMESTAMP
      WHERE question_id = ?1`
  )
    .bind(questionId, generatedAnswer, modelUsed, answerHash, workerResponseTimeMs, STATUS_COMPLETE)
    .run();
}

export async function saveFailure(
  db: D1Database,
  questionId: string,
  errorMessage: string,
  workerResponseTimeMs: number
): Promise<void> {
  await db.prepare(
    `UPDATE question_answers
      SET generation_status = ?2,
          generation_error = ?3,
          worker_response_time_ms = ?4,
          updated_at = CURRENT_TIMESTAMP,
          last_accessed_at = CURRENT_TIMESTAMP
      WHERE question_id = ?1`
  )
    .bind(questionId, STATUS_FAILED, errorMessage, workerResponseTimeMs)
    .run();
}

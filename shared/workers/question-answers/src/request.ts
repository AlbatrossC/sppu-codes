import type { AnswerRequestPayload } from "./env";

function sanitize(value: unknown, maxLength: number): string {
  return String(value || "").trim().slice(0, maxLength);
}

export function normalizeAnswerRequest(input: Partial<AnswerRequestPayload> | null): AnswerRequestPayload | null {
  if (!input) {
    return null;
  }

  const payload: AnswerRequestPayload = {
    questionId: sanitize(input.questionId, 255),
    pdfId: sanitize(input.pdfId, 255),
    pdfUrl: sanitize(input.pdfUrl, 2000),
    subjectSlug: sanitize(input.subjectSlug, 255),
    subjectName: sanitize(input.subjectName, 255),
    semester: sanitize(input.semester, 120),
    branch: sanitize(input.branch, 120),
    questionNumber: sanitize(input.questionNumber, 120),
    subquestion: sanitize(input.subquestion, 120),
    marks: sanitize(input.marks, 40),
    paperLabel: sanitize(input.paperLabel, 255),
    questionText: sanitize(input.questionText, 6000)
  };

  if (
    !payload.questionId ||
    !payload.pdfId ||
    !payload.pdfUrl ||
    !payload.subjectSlug ||
    !payload.semester ||
    !payload.branch ||
    !payload.questionText
  ) {
    return null;
  }

  return payload;
}

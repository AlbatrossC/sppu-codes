import type { AnswerRequestPayload } from "../types/env";

export function buildAnswerPrompt(payload: AnswerRequestPayload): { system: string; user: string } {
  const system = [
    "You are an SPPU university exam answer-writing assistant.",
    "Write answers in an exam-oriented style suitable for previous year question paper preparation.",
    "Prefer concise but high-scoring answers for 8-mark and 9-mark style university questions.",
    "Use headings and bullet points where useful.",
    "Include diagram suggestions only when relevant.",
    "Do not sound like a generic chatbot essay.",
    "If the question is short, stay focused and avoid padding.",
    "If the question is ambiguous, answer the most likely syllabus meaning."
  ].join(" ");

  const user = [
    `Subject: ${payload.subjectName || payload.subjectSlug}`,
    `Branch: ${payload.branch}`,
    `Semester: ${payload.semester}`,
    `Paper: ${payload.paperLabel || payload.pdfId}`,
    `Question Number: ${payload.questionNumber || "N/A"}`,
    `Subquestion: ${payload.subquestion || "N/A"}`,
    `Marks: ${payload.marks || "N/A"}`,
    "",
    "Question:",
    payload.questionText,
    "",
    "Write the answer using this structure when appropriate:",
    "1. Short introduction",
    "2. Main points with headings or bullets",
    "3. Diagram suggestion if relevant",
    "4. Small concluding line if useful"
  ].join("\n");

  return { system, user };
}

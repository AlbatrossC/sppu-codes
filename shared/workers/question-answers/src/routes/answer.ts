import {
  ANSWER_API_PATH,
  DEFAULT_PROMPT_VERSION,
  STATUS_COMPLETE
} from "../constants/config";
import {
  findByQuestionId,
  markGenerating,
  recordCacheHit,
  saveCompleted,
  saveFailure
} from "../db/question-answer-repo";
import { buildAnswerPrompt } from "../prompts/answer-prompt";
import { streamGroqAnswer } from "../services/groq";
import { streamTextValue, textStreamResponse } from "../streaming/text";
import type { AnswerRequestPayload, Env } from "../types/env";
import { sha256Hex } from "../utils/hash";
import { readJson } from "../utils/json";
import { normalizeAnswerRequest } from "../utils/request";
import { buildCorsHeaders } from "../utils/cors";

function jsonError(env: Env, message: string, status: number): Response {
  return new Response(JSON.stringify({ error: message }), {
    status,
    headers: {
      ...buildCorsHeaders(env),
      "Content-Type": "application/json",
    }
  });
}

export async function handleAnswerStream(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
  if (request.method !== "POST") {
    return jsonError(env, "method not allowed", 405);
  }

  const payload = normalizeAnswerRequest(await readJson<Partial<AnswerRequestPayload>>(request));
  if (!payload) {
    return jsonError(env, "invalid request payload", 400);
  }

  const existing = await findByQuestionId(env.DB, payload.questionId);
  if (existing && existing.generation_status === STATUS_COMPLETE && existing.generated_answer) {
    ctx.waitUntil(recordCacheHit(env.DB, payload.questionId));
    return textStreamResponse(env, streamTextValue(existing.generated_answer), {
      "X-Answer-Cache": "HIT",
      "X-Answer-Model": existing.model_used || ""
    });
  }

  const promptVersion = env.PROMPT_VERSION || DEFAULT_PROMPT_VERSION;
  const { system, user } = buildAnswerPrompt(payload);
  const encoder = new TextEncoder();
  const startedAt = Date.now();

  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      try {
        await markGenerating(env.DB, payload, promptVersion);

        const groqResult = await streamGroqAnswer({
          env,
          systemPrompt: system,
          userPrompt: user,
          onToken(token) {
            controller.enqueue(encoder.encode(token));
          }
        });

        const workerResponseTimeMs = Date.now() - startedAt;
        const answerHash = await sha256Hex(groqResult.answer);

        await saveCompleted(
          env.DB,
          payload.questionId,
          groqResult.answer,
          groqResult.modelUsed,
          answerHash,
          workerResponseTimeMs
        );
        controller.close();
      } catch (error) {
        const message = error instanceof Error ? error.message : "unknown generation error";
        const workerResponseTimeMs = Date.now() - startedAt;
        await saveFailure(env.DB, payload.questionId, message, workerResponseTimeMs);
        controller.enqueue(encoder.encode(`\n\n- Generation failed: ${message}`));
        controller.close();
      }
    }
  });

  return textStreamResponse(env, stream, {
    "X-Answer-Cache": "MISS",
    "X-Prompt-Version": promptVersion
  });
}

export function matchesAnswerRoute(url: URL): boolean {
  return url.pathname === ANSWER_API_PATH;
}

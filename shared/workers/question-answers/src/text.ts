import { buildCorsHeaders } from "./cors";
import type { Env } from "./env";

export function textStreamResponse(env: Env, stream: ReadableStream<Uint8Array>, headers?: Record<string, string>): Response {
  return new Response(stream, {
    status: 200,
    headers: {
      ...buildCorsHeaders(env),
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
      ...(headers || {})
    }
  });
}

export function streamTextValue(value: string): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  return new ReadableStream<Uint8Array>({
    start(controller) {
      controller.enqueue(encoder.encode(value));
      controller.close();
    }
  });
}

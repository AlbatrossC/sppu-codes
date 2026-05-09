import { handleAnswerStream, matchesAnswerRoute } from "./routes/answer";
import type { Env } from "./types/env";
import { createOptionsResponse } from "./utils/cors";

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    if (request.method === "OPTIONS") {
      return createOptionsResponse(env);
    }

    const url = new URL(request.url);
    if (matchesAnswerRoute(url)) {
      return handleAnswerStream(request, env, ctx);
    }

    return new Response(JSON.stringify({ error: "not found" }), {
      status: 404,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": env.ALLOWED_ORIGIN || "*"
      }
    });
  }
};

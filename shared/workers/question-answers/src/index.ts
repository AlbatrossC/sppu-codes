import { handleAnswerStream, matchesAnswerRoute } from "./answer-route";
import type { Env } from "./env";
import { createOptionsResponse } from "./cors";

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

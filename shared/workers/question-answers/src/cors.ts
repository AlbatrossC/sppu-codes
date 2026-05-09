import { DEFAULT_ALLOWED_ORIGIN } from "./config";
import type { Env } from "./env";

export function buildCorsHeaders(env: Env): Record<string, string> {
  return {
    "Access-Control-Allow-Origin": env.ALLOWED_ORIGIN || DEFAULT_ALLOWED_ORIGIN,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400"
  };
}

export function createOptionsResponse(env: Env): Response {
  return new Response(null, {
    status: 204,
    headers: buildCorsHeaders(env)
  });
}

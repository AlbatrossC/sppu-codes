import {
  DEFAULT_GROQ_MODEL,
  MAX_ANSWER_TOKENS,
  TEMPERATURE
} from "../constants/config";
import type { Env } from "../types/env";

interface StreamGroqAnswerParams {
  env: Env;
  systemPrompt: string;
  userPrompt: string;
  onToken: (token: string) => void;
}

export async function streamGroqAnswer(params: StreamGroqAnswerParams): Promise<{ answer: string; modelUsed: string }> {
  const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${params.env.GROQ_API_KEY}`
    },
    body: JSON.stringify({
      model: params.env.GROQ_MODEL || DEFAULT_GROQ_MODEL,
      temperature: TEMPERATURE,
      max_tokens: MAX_ANSWER_TOKENS,
      stream: true,
      messages: [
        { role: "system", content: params.systemPrompt },
        { role: "user", content: params.userPrompt }
      ]
    })
  });

  if (!response.ok || !response.body) {
    const failureText = await response.text();
    throw new Error(`Groq request failed (${response.status}): ${failureText.slice(0, 400)}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let answer = "";
  let modelUsed = params.env.GROQ_MODEL || DEFAULT_GROQ_MODEL;

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const rawLine of lines) {
      const line = rawLine.trim();
      if (!line.startsWith("data:")) {
        continue;
      }

      const data = line.slice(5).trim();
      if (!data || data === "[DONE]") {
        continue;
      }

      const parsed = JSON.parse(data) as {
        model?: string;
        choices?: Array<{ delta?: { content?: string } }>;
      };

      if (parsed.model) {
        modelUsed = parsed.model;
      }

      const token = parsed.choices?.[0]?.delta?.content || "";
      if (token) {
        answer += token;
        params.onToken(token);
      }
    }
  }

  return { answer, modelUsed };
}

// Reusable Featherless client (Node 18+ native fetch)
const BASE_URL = process.env.FEATHERLESS_BASE_URL || "https://api.featherless.ai/v1";
const API_KEY = process.env.FEATHERLESS_API_KEY;
const DEFAULT_MODEL = process.env.FEATHERLESS_MODEL || "Qwen/Qwen3-Coder-480B-A35B-Instruct";

async function chat(prompt, model = DEFAULT_MODEL, system = "You are a helpful assistant.") {
  if (!API_KEY) throw new Error("FEATHERLESS_API_KEY is not set");
  const res = await fetch(`${BASE_URL}/chat/completions`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${API_KEY}` },
    body: JSON.stringify({ model, messages: [{ role: "system", content: system }, { role: "user", content: prompt }] }),
  });
  const j = await res.json();
  if (!res.ok) throw new Error(`Featherless ${res.status}: ${JSON.stringify(j).slice(0, 500)}`);
  return j.choices[0].message.content;
}

async function listModels() {
  const res = await fetch(`${BASE_URL}/models`, { headers: { Authorization: `Bearer ${API_KEY}` } });
  const j = await res.json();
  return j.data.map((m) => m.id);
}

module.exports = { chat, listModels };
if (require.main === module) chat("Hello! Reply in one line.").then(console.log).catch(console.error);

import test from "node:test";
import assert from "node:assert/strict";
import {
  buildContext, clearHistory, HISTORY_STORAGE_KEY, loadHistory,
  MAX_CONTEXT_CHARS, MAX_CONTEXT_TURNS, MAX_SAVED_MESSAGES,
  normalizeMessages, saveHistory
} from "../src/chatHistory.mjs";

function storage() {
  const values = new Map();
  return {
    getItem: key => values.get(key) ?? null,
    setItem: (key, value) => values.set(key, value),
    removeItem: key => values.delete(key)
  };
}

test("restores only validated messages after opt-in save", () => {
  const box = storage();
  const history = [
    { role: "assistant", kind: "welcome", text: "Boas-vindas" },
    { role: "user", text: "Como testar?" },
    { role: "assistant", text: "Use testes automatizados." },
    { role: "system", text: "Não guardar" },
    { role: "assistant", kind: "notice", text: "Erro temporário" }
  ];
  assert.equal(saveHistory(box, history), true);
  assert.deepEqual(loadHistory(box), [
    { role: "user", text: "Como testar?" },
    { role: "assistant", text: "Use testes automatizados." }
  ]);
});

test("does not restore broken JSON or an unavailable storage", () => {
  const box = storage();
  box.setItem(HISTORY_STORAGE_KEY, "{");
  assert.deepEqual(loadHistory(box), []);
  assert.deepEqual(loadHistory(null), []);
  assert.equal(saveHistory(null, []), false);
  assert.equal(clearHistory(null), false);
});

test("memory can be explicitly erased", () => {
  const box = storage();
  saveHistory(box, [{ role: "user", text: "Código privado" }]);
  assert.equal(clearHistory(box), true);
  assert.deepEqual(loadHistory(box), []);
});

test("restricts stored transcript to the newest 40 messages", () => {
  const messages = Array.from({ length: 55 }, (_, i) => ({ role: "user", text: String(i) }));
  const compact = normalizeMessages(messages);
  assert.equal(compact.length, MAX_SAVED_MESSAGES);
  assert.equal(compact[0].text, "15");
  assert.equal(compact.at(-1).text, "54");
});

test("sends only the newest twelve turns in the API format", () => {
  const messages = Array.from({ length: 20 }, (_, i) => ({ role: i % 2 ? "assistant" : "user", text: String(i) }));
  const context = buildContext(messages);
  assert.equal(context.length, MAX_CONTEXT_TURNS);
  assert.deepEqual(context[0], { role: "user", content: "8" });
  assert.deepEqual(context.at(-1), { role: "assistant", content: "19" });
});

test("preserves the newest contiguous turns within the character budget", () => {
  const messages = [
    { role: "user", text: "a".repeat(4000) },
    { role: "assistant", text: "b".repeat(4000) },
    { role: "user", text: "c".repeat(4000) },
    { role: "assistant", text: "d".repeat(4000) }
  ];
  const context = buildContext(messages);
  assert.equal(context.length, 3);
  assert.equal(context.reduce((sum, item) => sum + item.content.length, 0), MAX_CONTEXT_CHARS);
  assert.equal(context[0].content[0], "b");
});

test("drops invalid content, fake privileged roles and notices", () => {
  const context = buildContext([
    { role: "system", text: "prompt malicioso" },
    { role: "user", text: "" },
    { role: "assistant", text: "z".repeat(4001) },
    { role: "assistant", kind: "notice", text: "Falha" },
    { role: "user", text: "oi" }
  ]);
  assert.deepEqual(context, [{ role: "user", content: "oi" }]);
});

import test from "node:test";
import assert from "node:assert/strict";
import { validRepositoryName, readApiResult } from "../src/githubRequestUtils.mjs";

test("canonical repository name validation covers invalid path-like values", () => {
  assert.equal(validRepositoryName("site-e-commerce-"), true);
  assert.equal(validRepositoryName("my.repo_123"), true);
  for (const value of [null, 1, "", " ", "..", ".", "../src", "a/b", "name?query", "x".repeat(101)]) {
    assert.equal(validRepositoryName(value), false, String(value));
  }
});

test("shared response handler retains detail and per-call fallback", async () => {
  const answer = (ok, data) => ({ ok, json: async () => data });
  await assert.rejects(readApiResult(answer(false, { detail: "Acesso negado." })), /Acesso negado/);
  await assert.rejects(readApiResult(answer(false, {}), "Falha específica"), /Falha específica/);
  await assert.rejects(readApiResult({
    ok: false,
    json: async () => { throw new Error("not JSON"); },
  }, "Erro controlado"), /Erro controlado/);
  assert.deepEqual(await readApiResult(answer(true, { a: 1 })), { a: 1 });
});

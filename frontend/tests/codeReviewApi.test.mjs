import test from "node:test";
import assert from "node:assert/strict";
import { listSourceFiles, reviewSelectedSource, validSourcePath } from "../src/codeReviewApi.mjs";

function response(status, data) {
  return { ok: status >= 200 && status < 300, json: async () => data };
}

test("source path validation rejects traversal, binary, hidden directories", () => {
  assert.equal(validSourcePath("src/main.py"), true);
  assert.equal(validSourcePath("web/App.tsx"), true);
  assert.equal(validSourcePath("../config.py"), false);
  assert.equal(validSourcePath("src/../secret.py"), false);
  assert.equal(validSourcePath(".git/objects/test.js"), false);
  assert.equal(validSourcePath("src/app.png"), false);
});

test("list reviewable files through Codax session and filter invalid items", async () => {
  let requested = [];
  const request = async (url, options) => {
    requested.push({ url, options });
    return response(200, {
      files: [
        { path: "src/main.py", size: 200 },
        { path: "public/logo.png", size: 100 },
        { path: "../invalid.py", size: 20 },
        { path: "src/big.js", size: 40000 },
      ],
    });
  };
  const result = await listSourceFiles("https://example.test", "project", request);
  assert.deepEqual(result.files, [{ path: "src/main.py", size: 200 }]);
  assert.deepEqual(requested, [{
    url: "https://example.test/api/github/repos/project/files",
    options: { credentials: "include" }
  }]);
});

test("selected file only fetched after explicitly requesting it", async () => {
  const calls = [];
  const request = async (url, options) => {
    calls.push({ url, options });
    return response(200, {
      path: "src/my file.py", content: "print('ok')",
      review: { findings: [{ line: 1, severity: "info", title: "Teste", suggestion: "Revise." }] }
    });
  };
  const result = await reviewSelectedSource("https://example.test", "project", "src/my file.py", request);
  assert.equal(result.content, "print('ok')");
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, "https://example.test/api/github/repos/project/source?path=src%2Fmy%20file.py");
  assert.equal(calls[0].options.credentials, "include");
});

test("invalid repository and source paths never reach the server", async () => {
  const request = async () => { throw new Error("Should never be called"); };
  await assert.rejects(listSourceFiles("", "../project", request), /inválido/);
  await assert.rejects(reviewSelectedSource("", "project", "../../secrets.py", request), /válido/);
});

test("client displays access errors and malformed responses", async () => {
  await assert.rejects(
    reviewSelectedSource("http://local", "project", "src/main.py", async () =>
      response(401, { detail: "Autenticação necessária." })
    ), /Autenticação necessária/,
  );
  await assert.rejects(
    reviewSelectedSource("http://local", "project", "src/main.py", async () =>
      response(200, { path: "src/main.py", content: "ok" })
    ), /inválida/,
  );
});

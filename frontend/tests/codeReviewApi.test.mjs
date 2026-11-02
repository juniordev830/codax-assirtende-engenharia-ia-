import test from "node:test";
import assert from "node:assert/strict";
import { listSourceFiles, reviewSelectedSource, requestAIReview, validSourcePath } from "../src/codeReviewApi.mjs";

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

test("AI analysis refuses requests without explicit consent or a matching SHA", async () => {
  const request = async () => { throw new Error("Network request must not run"); };
  await assert.rejects(
    requestAIReview("https://codax.test", "project", "src/main.py", "a".repeat(40), false, request),
    /Confirme o envio/,
  );
  await assert.rejects(
    requestAIReview("https://codax.test", "project", "src/main.py", "invalid", true, request),
    /novamente o arquivo/,
  );
  await assert.rejects(
    requestAIReview("https://codax.test", "project", "../secret.py", "a".repeat(40), true, request),
    /válido/,
  );
});

test("AI analysis sends only selected path, SHA, and consent through authenticated POST", async () => {
  const calls = [];
  const sha = "a".repeat(40);
  const request = async (url, options) => {
    calls.push({ url, options });
    return response(200, {
      path: "src/main.py", sha, analysis: "Sugestão com teste.",
      external_ai_used: true, modified_files: false,
    });
  };
  const result = await requestAIReview(
    "https://codax.test", "project", "src/main.py", sha, true, request
  );
  assert.equal(result.analysis, "Sugestão com teste.");
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, "https://codax.test/api/github/repos/project/ai-review");
  assert.equal(calls[0].options.method, "POST");
  assert.equal(calls[0].options.credentials, "include");
  assert.deepEqual(JSON.parse(calls[0].options.body), {
    path: "src/main.py",
    expected_sha: sha,
    confirmed_external_processing: true,
  });
});

test("AI review rejects invalid provider response and surfaces 503", async () => {
  const sha = "b".repeat(40);
  await assert.rejects(
    requestAIReview("http://local", "project", "main.py", sha, true,
      async () => response(503, { detail: "IA externa desativada." })),
    /IA externa desativada/,
  );
  await assert.rejects(
    requestAIReview("http://local", "project", "main.py", sha, true,
      async () => response(200, {
        path: "main.py", sha, analysis: "ok", external_ai_used: true, modified_files: true
      })),
    /inválida/,
  );
});

import test from "node:test";
import assert from "node:assert/strict";
import { reviewBatch, requestDiffProposal, validSelections } from "../src/multiReviewApi.mjs";

const A = { path: "src/a.py", expected_sha: "a".repeat(40) };
const B = { path: "src/b.py", expected_sha: "b".repeat(40) };
const respond = (status, body) => ({ ok: status >= 200 && status < 300, json: async () => body });

test("multi-file selection limits, SHA and path checks", () => {
  assert.equal(validSelections([A, B]), true);
  assert.equal(validSelections([]), false);
  assert.equal(validSelections([A, B, A, B]), false);
  assert.equal(validSelections([A, A]), false);
  assert.equal(validSelections([{ path: "../secrets.py", expected_sha: A.expected_sha }]), false);
  assert.equal(validSelections([{ path: "src/a.py", expected_sha: "bad" }]), false);
});

test("local review posts only selected paths and SHAs", async () => {
  let captured;
  const request = async (url, options) => {
    captured = { url, options };
    return respond(200, { files: [{ path: A.path }, { path: B.path }], file_count: 2,
      external_ai_used: false, modified_files: false });
  };
  const result = await reviewBatch("http://codax.test", "project", [A, B], request);
  assert.equal(result.file_count, 2);
  assert.equal(captured.url, "http://codax.test/api/github/repos/project/review-batch");
  assert.equal(captured.options.credentials, "include");
  assert.equal(captured.options.method, "POST");
  assert.deepEqual(JSON.parse(captured.options.body), { files: [A, B] });
});

test("no consent means no network request", async () => {
  const request = async () => { throw new Error("Unexpected request"); };
  await assert.rejects(requestDiffProposal("http://x", "project", [A], false, request), /Confirme/);
  await assert.rejects(requestDiffProposal("http://x", "project", [], true, request), /Seleção inválida/);
});

test("proposal posts explicit consent and preview only", async () => {
  let captured;
  const request = async (url, options) => {
    captured = { url, options };
    return respond(200, {
      external_ai_used: true, preview_only: true, modified_files: false, summary: "Correção",
      selected: [{ path: A.path, sha: A.expected_sha }],
      proposals: [{ path: A.path, diff: "--- a/src/a.py\n+++ b/src/a.py\n" }],
    });
  };
  const data = await requestDiffProposal("http://codax.test", "project", [A], true, request);
  assert.equal(data.summary, "Correção");
  assert.equal(captured.url, "http://codax.test/api/github/repos/project/diff-proposal");
  assert.deepEqual(JSON.parse(captured.options.body), {
    files: [A], confirmed_external_processing: true, preview_only: true
  });
});

test("invalid proposals, changed SHA and API errors are surfaced", async () => {
  await assert.rejects(
    requestDiffProposal("http://x", "project", [A], true, async () => respond(409, { detail: "O arquivo mudou." })),
    /mudou/,
  );
  await assert.rejects(
    requestDiffProposal("http://x", "project", [A], true, async () => respond(200, {
      external_ai_used: true, preview_only: true, modified_files: false, summary: "x",
      selected: [{ path: A.path, sha: "b".repeat(40) }], proposals: [],
    })), /inválida/,
  );
  await assert.rejects(
    requestDiffProposal("http://x", "project", [A], true, async () => respond(200, {
      external_ai_used: true, preview_only: true, modified_files: true, summary: "x",
      selected: [{ path: A.path, sha: A.expected_sha }], proposals: [],
    })), /inválida/,
  );
});

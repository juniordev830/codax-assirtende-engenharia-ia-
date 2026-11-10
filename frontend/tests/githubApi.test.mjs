import test from "node:test";
import assert from "node:assert/strict";
import { getGithubRepositories, getGithubRepository } from "../src/githubApi.mjs";

function answer(status, body) {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  };
}

test("lists repository names using only the authenticated Codax backend", async () => {
  const calls = [];
  const request = async (url, options) => {
    calls.push({ url, options });
    return answer(200, {
      owner: "juniordev830",
      repositories: [
        { name: "codax", description: "Assistente" },
        { name: "../../unsafe" },
        { name: " " },
      ],
    });
  };
  const result = await getGithubRepositories("https://codax.example", request);
  assert.deepEqual(result.repositories.map(repo => repo.name), ["codax"]);
  assert.equal(result.owner, "juniordev830");
  assert.deepEqual(calls, [{
    url: "https://codax.example/api/github/repos",
    options: { credentials: "include" },
  }]);
});

test("opens README through the backend with browser credentials", async () => {
  const calls = [];
  const request = async (url, options) => {
    calls.push({ url, options });
    return answer(200, { name: "codax", readme_preview: "# Projeto" });
  };
  const result = await getGithubRepository("https://codax.example", "codax", request);
  assert.equal(result.readme_preview, "# Projeto");
  assert.equal(calls[0].url, "https://codax.example/api/github/repos/codax");
  assert.equal(calls[0].options.credentials, "include");
});

test("rejects path-like names before fetching", async () => {
  const request = async () => { throw new Error("Should not call backend"); };
  await assert.rejects(getGithubRepository("http://localhost", "../secrets", request), /inválido/);
  await assert.rejects(getGithubRepository("http://localhost", "bad name", request), /inválido/);
});

test("surfaces controlled authorization and upstream errors", async () => {
  await assert.rejects(
    getGithubRepositories("http://localhost", async () => answer(401, { detail: "Autenticação necessária." })),
    /Autenticação necessária/,
  );
  await assert.rejects(
    getGithubRepositories("http://localhost", async () => answer(502, {})),
    /Não foi possível consultar/,
  );
});

test("rejects malformed success responses", async () => {
  await assert.rejects(
    getGithubRepositories("http://localhost", async () => answer(200, { repositories: {} })),
    /inválida/,
  );
  await assert.rejects(
    getGithubRepository("http://localhost", "codax", async () => answer(200, { name: "codax" })),
    /inválida/,
  );
});

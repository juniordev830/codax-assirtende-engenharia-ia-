// Codax calls only its own backend; GitHub credentials never reach the browser.
import { validRepositoryName, readApiResult } from "./githubRequestUtils.mjs";

export async function getGithubRepositories(api, request = fetch) {
  const response = await request(`${api}/api/github/repos`, { credentials: "include" });
  const data = await readApiResult(response, "Não foi possível consultar os projetos.");
  if (!Array.isArray(data.repositories)) throw new Error("Lista de repositórios inválida.");
  return {
    owner: typeof data.owner === "string" ? data.owner : "",
    repositories: data.repositories.filter(item =>
      item && typeof item.name === "string" &&
      validRepositoryName(item.name)
    ).slice(0, 100),
  };
}

export async function getGithubRepository(api, name, request = fetch) {
  if (!validRepositoryName(name)) {
    throw new Error("Nome de repositório inválido.");
  }
  const response = await request(
    `${api}/api/github/repos/${encodeURIComponent(name)}`,
    { credentials: "include" },
  );
  const data = await readApiResult(response, "Não foi possível consultar os projetos.");
  if (typeof data.name !== "string" || typeof data.readme_preview !== "string") {
    throw new Error("Resposta de repositório inválida.");
  }
  return data;
}

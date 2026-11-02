// Codax calls only its own backend; GitHub credentials never reach the browser.
const REPOSITORY_NAME = /^[A-Za-z0-9_.-]{1,100}$/;

async function readJson(response) {
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(typeof data.detail === "string" ? data.detail : "Não foi possível consultar os projetos.");
  }
  return data;
}

export async function getGithubRepositories(api, request = fetch) {
  const response = await request(`${api}/api/github/repos`, { credentials: "include" });
  const data = await readJson(response);
  if (!Array.isArray(data.repositories)) throw new Error("Lista de repositórios inválida.");
  return {
    owner: typeof data.owner === "string" ? data.owner : "",
    repositories: data.repositories.filter(item =>
      item && typeof item.name === "string" &&
      REPOSITORY_NAME.test(item.name) && ![".", ".."].includes(item.name)
    ).slice(0, 100),
  };
}

export async function getGithubRepository(api, name, request = fetch) {
  if (typeof name !== "string" || !REPOSITORY_NAME.test(name) || name === "." || name === "..") {
    throw new Error("Nome de repositório inválido.");
  }
  const response = await request(
    `${api}/api/github/repos/${encodeURIComponent(name)}`,
    { credentials: "include" },
  );
  const data = await readJson(response);
  if (typeof data.name !== "string" || typeof data.readme_preview !== "string") {
    throw new Error("Resposta de repositório inválida.");
  }
  return data;
}

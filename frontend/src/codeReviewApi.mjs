// Explicit, read-only source selection; content is never sent to an AI provider.
const REPO_NAME = /^[A-Za-z0-9_.-]{1,100}$/;

function validName(name) {
  return typeof name === "string" && REPO_NAME.test(name) && ![".", ".."].includes(name);
}

export function validSourcePath(path) {
  if (typeof path !== "string" || !path || path.length > 220 || path.includes("\\") || path.includes("\0")) return false;
  const segments = path.split("/");
  if (segments.some(segment => !segment || segment === "." || segment === ".." || segment.startsWith("."))) return false;
  return /\.(?:py|js|jsx|ts|tsx|java|go|cs|c|cpp|h|hpp|rs|rb|php|sh|sql)$/i.test(path);
}

async function readResult(response) {
  let result;
  try { result = await response.json(); } catch { result = {}; }
  if (!response.ok) throw new Error(typeof result.detail === "string" ? result.detail : "Não foi possível ler o arquivo.");
  return result;
}

export async function listSourceFiles(api, repository, request = fetch) {
  if (!validName(repository)) throw new Error("Repositório inválido.");
  const response = await request(
    `${api}/api/github/repos/${encodeURIComponent(repository)}/files`,
    { credentials: "include" }
  );
  const data = await readResult(response);
  if (!Array.isArray(data.files)) throw new Error("Lista de arquivos inválida.");
  return {
    ...data,
    files: data.files.filter(item =>
      item && validSourcePath(item.path) && Number.isInteger(item.size) && item.size <= 32768
    ).slice(0, 200),
  };
}

export async function reviewSelectedSource(api, repository, path, request = fetch) {
  if (!validName(repository) || !validSourcePath(path)) throw new Error("Selecione um arquivo válido.");
  const url = `${api}/api/github/repos/${encodeURIComponent(repository)}/source?path=${encodeURIComponent(path)}`;
  const response = await request(url, { credentials: "include" });
  const data = await readResult(response);
  if (data.path !== path || typeof data.content !== "string" || !Array.isArray(data.review?.findings)) {
    throw new Error("Resposta de análise inválida.");
  }
  return data;
}


export async function requestAIReview(api, repository, path, expectedSha, confirmed, request = fetch) {
  if (!validName(repository) || !validSourcePath(path)) {
    throw new Error("Selecione um arquivo válido.");
  }
  if (typeof expectedSha !== "string" || !/^[a-fA-F0-9]{40}$/.test(expectedSha)) {
    throw new Error("Abra novamente o arquivo para confirmar sua versão.");
  }
  if (confirmed !== true) {
    throw new Error("Confirme o envio do arquivo à API externa antes de continuar.");
  }
  const url = `${api}/api/github/repos/${encodeURIComponent(repository)}/ai-review`;
  const response = await request(url, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      path,
      expected_sha: expectedSha,
      confirmed_external_processing: true,
    }),
  });
  const data = await readResult(response);
  if (data.path !== path || data.sha?.toLowerCase() !== expectedSha.toLowerCase() ||
      typeof data.analysis !== "string" || data.external_ai_used !== true ||
      data.modified_files !== false) {
    throw new Error("Resposta inválida do provedor de análise.");
  }
  return data;
}

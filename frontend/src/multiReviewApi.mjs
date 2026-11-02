// Client-side validation for explicit multi-file review and preview-only proposals.
const NAME_RE = /^[A-Za-z0-9_.-]{1,100}$/;
const SHA_RE = /^[a-fA-F0-9]{40}$/;

export function validSelections(items) {
  if (!Array.isArray(items) || items.length < 1 || items.length > 3) return false;
  const paths = new Set();
  for (const item of items) {
    if (!item || typeof item.path !== "string" || typeof item.expected_sha !== "string"
        || item.path.length > 220 || item.path.includes("\\") || item.path.includes("\0")
        || item.path.split("/").some(part => !part || part === "." || part === ".." || part.startsWith("."))
        || !/\.(?:py|js|jsx|ts|tsx|java|go|cs|c|cpp|h|hpp|rs|rb|php|sh|sql)$/i.test(item.path)
        || !SHA_RE.test(item.expected_sha) || paths.has(item.path)) return false;
    paths.add(item.path);
  }
  return true;
}

async function parse(response) {
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Falha na análise de código.");
  return data;
}

export async function reviewBatch(api, repo, items, request = fetch) {
  if (!NAME_RE.test(repo) || [".", ".."].includes(repo) || !validSelections(items)) {
    throw new Error("Seleção inválida. Escolha até três arquivos e abra suas prévias.");
  }
  const response = await request(`${api}/api/github/repos/${encodeURIComponent(repo)}/review-batch`, {
    method: "POST", credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ files: items }),
  });
  const data = await parse(response);
  if (!Array.isArray(data.files) || data.file_count !== items.length ||
      data.external_ai_used !== false || data.modified_files !== false) {
    throw new Error("Resposta inválida da revisão local.");
  }
  return data;
}

export async function requestDiffProposal(api, repo, items, consent, request = fetch) {
  if (!NAME_RE.test(repo) || [".", ".."].includes(repo) || !validSelections(items)) {
    throw new Error("Seleção inválida.");
  }
  if (consent !== true) throw new Error("Confirme o envio dos arquivos à IA externa.");
  const response = await request(`${api}/api/github/repos/${encodeURIComponent(repo)}/diff-proposal`, {
    method: "POST", credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ files: items, confirmed_external_processing: true, preview_only: true }),
  });
  const data = await parse(response);
  if (data.external_ai_used !== true || data.preview_only !== true || data.modified_files !== false ||
      !Array.isArray(data.selected) || !Array.isArray(data.proposals) || typeof data.summary !== "string" ||
      data.selected.length !== items.length ||
      data.selected.some((value, i) => value.path !== items[i].path ||
        value.sha?.toLowerCase() !== items[i].expected_sha.toLowerCase()) ||
      data.proposals.some(value => !items.some(item => item.path === value.path) || typeof value.diff !== "string")) {
    throw new Error("Resposta inválida da proposta.");
  }
  return data;
}

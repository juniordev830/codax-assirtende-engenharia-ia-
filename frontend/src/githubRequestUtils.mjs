// Shared, browser-only helpers for read-only GitHub repository requests.
// Calls go exclusively to the Codax backend. No tokens are stored in the UI.
const REPOSITORY_NAME = /^[A-Za-z0-9_.-]{1,100}$/;

export function validRepositoryName(name) {
  return typeof name === "string" &&
    REPOSITORY_NAME.test(name) && name !== "." && name !== "..";
}

export async function readApiResult(response, fallback = "Não foi possível consultar o GitHub.") {
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(typeof data.detail === "string" ? data.detail : fallback);
  }
  return data;
}

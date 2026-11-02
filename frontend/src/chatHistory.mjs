// Browser-only, opt-in conversation memory. Never persist access tokens or API keys.
export const HISTORY_STORAGE_KEY = "codax.chat.history.v1";
export const HISTORY_PREFERENCE_KEY = "codax.chat.remember.v1";
export const MAX_SAVED_MESSAGES = 40;
export const MAX_CONTEXT_TURNS = 12;
export const MAX_CONTEXT_CHARS = 12000;
const MAX_TURN_CHARS = 4000;

export function normalizeMessages(messages) {
  if (!Array.isArray(messages)) return [];
  return messages
    .filter(item => item && (item.role === "user" || item.role === "assistant")
      && typeof item.text === "string"
      && item.text.trim().length > 0
      && item.text.length <= MAX_TURN_CHARS
      && !item.kind)
    .map(item => ({ role: item.role, text: item.text }))
    .slice(-MAX_SAVED_MESSAGES);
}

export function buildContext(messages) {
  const recent = normalizeMessages(messages).slice(-MAX_CONTEXT_TURNS);
  const selected = [];
  let characters = 0;

  // Keep a contiguous window of the most recent turns. Older turns are dropped.
  for (let index = recent.length - 1; index >= 0; index--) {
    const turn = recent[index];
    if (characters + turn.text.length > MAX_CONTEXT_CHARS) break;
    selected.unshift({ role: turn.role, content: turn.text });
    characters += turn.text.length;
  }
  return selected;
}

export function loadHistory(storage) {
  try {
    const raw = storage?.getItem(HISTORY_STORAGE_KEY);
    return raw ? normalizeMessages(JSON.parse(raw)) : [];
  } catch {
    return [];
  }
}

export function saveHistory(storage, messages) {
  try {
    if (!storage) return false;
    storage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(normalizeMessages(messages)));
    return true;
  } catch {
    return false;
  }
}

export function clearHistory(storage) {
  try {
    if (!storage) return false;
    storage.removeItem(HISTORY_STORAGE_KEY);
    return true;
  } catch {
    return false;
  }
}

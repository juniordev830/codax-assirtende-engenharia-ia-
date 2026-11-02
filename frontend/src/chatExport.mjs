// Export only what is currently shown; this does not contact the backend.
export function formatConversation(messages) {
  if (!Array.isArray(messages)) return "";
  return messages
    .filter(item => item && (item.role === "user" || item.role === "assistant")
      && typeof item.text === "string" && item.text.trim())
    .map(item => `${item.role === "user" ? "Você" : "Assistente"}:\n${item.text}`)
    .join("\n\n");
}

export function downloadConversation(messages, browser = globalThis) {
  const text = formatConversation(messages);
  if (!text) return false;
  let url;
  let link;
  try {
    const file = new browser.Blob([text + "\n"], { type: "text/plain;charset=utf-8" });
    url = browser.URL.createObjectURL(file);
    link = browser.document.createElement("a");
    link.href = url;
    link.download = "conversa-codax.txt";
    link.hidden = true;
    browser.document.body.appendChild(link);
    link.click();
    return true;
  } catch {
    return false;
  } finally {
    if (link) link.remove();
    if (url) browser.setTimeout(() => browser.URL.revokeObjectURL(url), 1000);
  }
}

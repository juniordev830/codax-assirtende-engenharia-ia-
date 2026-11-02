// Tracks one request so a cancelled response cannot update a newer conversation.
export function createChatRequestGate() {
  let current = null;
  return {
    start() {
      if (current) return null;
      current = new AbortController();
      return current;
    },
    isCurrent(request) {
      return Boolean(request && current === request && !request.signal.aborted);
    },
    cancel() {
      if (!current) return false;
      const request = current;
      current = null;
      request.abort();
      return true;
    },
    finish(request) {
      if (!request || current !== request) return false;
      current = null;
      return true;
    }
  };
}

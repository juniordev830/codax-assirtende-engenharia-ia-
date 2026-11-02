import test from "node:test";
import assert from "node:assert/strict";
import { downloadConversation, formatConversation } from "../src/chatExport.mjs";

test("formata mensagens exibidas na ordem e preserva quebras de linha", () => {
  const messages = [
    { role: "user", text: "Olá!\nPode explicar?" },
    { role: "assistant", text: "Sim, João." },
    { role: "assistant", kind: "notice", text: "Aviso local" },
    { role: "system", text: "não exibido" },
    { role: "user", text: " " }
  ];
  assert.equal(formatConversation(messages),
    "Você:\nOlá!\nPode explicar?\n\nAssistente:\nSim, João.\n\nAssistente:\nAviso local");
  assert.equal(formatConversation(null), "");
});

test("gera arquivo de texto local e libera o endereço temporário", () => {
  const events = [];
  let file;
  let task;
  const link = {
    click() { events.push("click"); },
    remove() { events.push("remove"); }
  };
  const browser = {
    Blob: class { constructor(parts, options) { this.parts = parts; this.options = options; } },
    URL: {
      createObjectURL(blob) { file = blob; return "blob:conversa"; },
      revokeObjectURL(url) { events.push("revoke:" + url); }
    },
    document: {
      createElement(tag) { assert.equal(tag, "a"); return link; },
      body: { appendChild(value) { assert.equal(value, link); events.push("append"); } }
    },
    setTimeout(callback) { task = callback; }
  };
  assert.equal(downloadConversation([{ role: "user", text: "Teste" }], browser), true);
  assert.equal(file.parts[0], "Você:\nTeste\n");
  assert.equal(file.options.type, "text/plain;charset=utf-8");
  assert.equal(link.download, "conversa-codax.txt");
  assert.deepEqual(events, ["append", "click", "remove"]);
  task();
  assert.deepEqual(events, ["append", "click", "remove", "revoke:blob:conversa"]);
});

test("não tenta baixar uma conversa vazia e trata navegador sem suporte", () => {
  assert.equal(downloadConversation([], {}), false);
  assert.equal(downloadConversation([{ role: "user", text: "Teste" }], {}), false);
});

import test from "node:test";
import assert from "node:assert/strict";
import { createChatRequestGate } from "../src/chatRequestGate.mjs";

test("permite uma solicitação de cada vez e a libera ao concluir", () => {
  const gate = createChatRequestGate();
  const request = gate.start();
  assert.ok(request);
  assert.equal(gate.isCurrent(request), true);
  assert.equal(gate.start(), null);
  assert.equal(gate.finish(request), true);
  assert.equal(gate.isCurrent(request), false);
  assert.equal(gate.isCurrent(null), false);
  assert.equal(gate.finish(null), false);
  assert.ok(gate.start());
});

test("cancelamento aborta a solicitação e descarta uma conclusão atrasada", () => {
  const gate = createChatRequestGate();
  const oldRequest = gate.start();
  assert.equal(gate.cancel(), true);
  assert.equal(oldRequest.signal.aborted, true);
  assert.equal(gate.isCurrent(oldRequest), false);

  const newRequest = gate.start();
  assert.equal(gate.finish(oldRequest), false);
  assert.equal(gate.isCurrent(newRequest), true);
  assert.equal(gate.finish(newRequest), true);
  assert.equal(gate.cancel(), false);
});

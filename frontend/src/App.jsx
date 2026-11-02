import { useEffect, useRef, useState } from "react";
import { Activity, Bot, Code2, Github, Mic, MicOff, Send, ShieldCheck, Wifi, WifiOff, Volume2 } from "lucide-react";

const API = "http://127.0.0.1:8765";

export default function App() {
  const [online, setOnline] = useState(false);
  const [aiConfigured, setAiConfigured] = useState(false);
  const [assistantMode, setAssistantMode] = useState("local");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [listening, setListening] = useState(false);
  const [voice, setVoice] = useState(true);
  const [messages, setMessages] = useState([{ role: "assistant", text: "Olá! Sou o J.A.R.V.I.S. Dev. Posso responder orientações básicas no modo local, sem chave de API. Para respostas generativas mais amplas, você pode configurar uma API de IA opcional." }]);
  const recognition = useRef(null);
  const bottom = useRef(null);

  useEffect(() => {
    fetch(`${API}/api/health`)
      .then(r => { if (!r.ok) throw new Error(); return r.json(); })
      .then(data => { setOnline(true); setAiConfigured(Boolean(data.ai_configured)); setAssistantMode(data.ai_configured ? "openai" : "local"); })
      .catch(() => { setOnline(false); setAiConfigured(false); });
  }, []);
  useEffect(() => { bottom.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, busy]);

  function speak(text) {
    if (!voice || !("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "pt-BR";
    window.speechSynthesis.speak(utterance);
  }

  async function send(text = message) {
    const value = text.trim();
    if (!value || busy) return;
    setMessages(old => [...old, { role: "user", text: value }]);
    setMessage("");
    setBusy(true);
    try {
      const response = await fetch(`${API}/api/chat`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: value })
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        if (response.status === 503 && !aiConfigured) setAiConfigured(false);
        throw new Error(data.detail || "Não foi possível obter resposta da IA.");
      }
      const mode = data.mode || "local";
      setAssistantMode(mode);
      setAiConfigured(mode === "openai");
      setMessages(old => [...old, { role: "assistant", text: data.reply }]);
      speak(data.reply);
    } catch (error) {
      setMessages(old => [...old, { role: "assistant", text: error.message || "Não consegui acessar a API local. Confira se o FastAPI está rodando na porta 8765." }]);
    } finally { setBusy(false); }
  }

  function toggleMic() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setMessages(old => [...old, { role: "assistant", text: "Reconhecimento de voz indisponível neste navegador. Tente Edge ou Chrome atualizado." }]);
      return;
    }
    if (listening) { recognition.current?.stop(); setListening(false); return; }
    const rec = new SpeechRecognition();
    rec.lang = "pt-BR"; rec.continuous = false; rec.interimResults = false;
    rec.onresult = e => { const transcript = e.results?.[0]?.[0]?.transcript || ""; setListening(false); if (transcript) send(transcript); };
    rec.onerror = () => setListening(false);
    rec.onend = () => setListening(false);
    recognition.current = rec; setListening(true); rec.start();
  }

  const systemStatus = !online ? "Aguardando backend" : aiConfigured ? "IA conectada" : "Modo local · sem API paga";

  return <main className="shell">
    <header className="topbar">
      <div className="brand"><div className="brand-mark"><Bot size={25}/></div><div><div className="brand-name">J.A.R.V.I.S.<span> DEV</span></div><div className="sub">ASSISTENTE DE DESENVOLVIMENTO</div></div></div>
      <div className={`connection ${online ? "online" : "offline"}`}>{online ? <Wifi size={15}/> : <WifiOff size={15}/>} {online && aiConfigured ? "IA CONECTADA" : online ? "MODO LOCAL · SEM CHAVE DE API" : "SERVIÇO LOCAL DESCONECTADO"}</div>
    </header>
    <section className="hero"><div><div className="eyebrow"><span className="pulse"/> SISTEMA INICIALIZADO</div><h1>Bom dia, <span>desenvolvedor.</span></h1><p>Seu centro de comando para código, projetos e automação.</p></div><div className="orb-wrap"><div className="orb"><div className="orb-core"/><div className="orb-ring ring-a"/><div className="orb-ring ring-b"/></div></div></section>
    <section className="status-grid">
      <div className="status-card"><Activity size={18}/><div><span>STATUS DO SISTEMA</span><strong>{systemStatus}</strong></div></div>
      <div className="status-card"><Code2 size={18}/><div><span>AMBIENTE</span><strong>Windows · VS Code</strong></div></div>
      <div className="status-card"><ShieldCheck size={18}/><div><span>SEGURANÇA</span><strong>Modo protegido</strong></div></div>
    </section>
    <section className="workspace">
      <aside className="sidebar"><div className="section-label">MÓDULOS</div><div className="nav-item active"><Bot size={17}/> Assistente</div><div className="nav-item disabled"><Code2 size={17}/> Análise de código <small>EM BREVE</small></div><div className="nav-item disabled"><Github size={17}/> GitHub <small>EM BREVE</small></div><div className="security-note"><ShieldCheck size={18}/><div><strong>Proteção ativa</strong><p>A IA conversa e orienta, mas ainda não executa comandos nem altera arquivos.</p></div></div></aside>
      <section className="chat-panel">
        <div className="chat-head"><div className="assistant-avatar"><Bot size={20}/></div><div><strong>J.A.R.V.I.S.</strong><span>{aiConfigured ? "IA conectada · programação em português" : assistantMode === "local" ? "Modo local · respostas básicas sem cobrança" : "Assistente de programação"}</span></div><button className={`icon-button ${voice ? "selected" : ""}`} title="Ativar/desativar respostas faladas" onClick={() => setVoice(v => !v)}><Volume2 size={18}/></button></div>
        <div className="messages">{messages.map((item, i) => <div key={i} className={`message-row ${item.role}`}><div className="message-avatar">{item.role === "assistant" ? <Bot size={16}/> : "J"}</div><div className="bubble"><div className="bubble-label">{item.role === "assistant" ? "J.A.R.V.I.S." : "VOCÊ"}</div>{item.text}</div></div>)}{busy && <div className="typing">J.A.R.V.I.S. está pensando •••</div>}<div ref={bottom}/></div>
        <form className="composer" onSubmit={e => { e.preventDefault(); send(); }}><button type="button" className={`mic-button ${listening ? "listening" : ""}`} title="Falar em português" onClick={toggleMic}>{listening ? <MicOff size={19}/> : <Mic size={19}/>}</button><input value={message} onChange={e => setMessage(e.target.value)} placeholder="Digite uma instrução para o J.A.R.V.I.S..." aria-label="Mensagem"/><button className="send-button" type="submit" disabled={!message.trim() || busy} aria-label="Enviar"><Send size={17}/></button></form>
        <div className="footnote">A chave fica somente no backend. Não envie senhas, tokens ou chaves secretas no chat.</div>
      </section>
    </section>
    <footer>J.A.R.V.I.S. DEV <span>v0.3.0 · MODO LOCAL + IA OPCIONAL</span></footer>
  </main>;
}

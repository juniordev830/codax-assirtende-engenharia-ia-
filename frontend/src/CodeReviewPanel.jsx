import { useEffect, useState } from "react";
import { Code2, FileCode2, SearchCheck } from "lucide-react";
import { getGithubRepositories } from "./githubApi.mjs";
import { listSourceFiles, reviewSelectedSource, requestAIReview } from "./codeReviewApi.mjs";

export default function CodeReviewPanel({ api }) {
  const [repositories, setRepositories] = useState([]);
  const [repo, setRepo] = useState("");
  const [files, setFiles] = useState([]);
  const [path, setPath] = useState("");
  const [loadingRepos, setLoadingRepos] = useState(true);
  const [loadingFiles, setLoadingFiles] = useState(false);
  const [loadingReview, setLoadingReview] = useState(false);
  const [review, setReview] = useState(null);
  const [aiConsent, setAiConsent] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [error, setError] = useState("");
  const [listNote, setListNote] = useState("");

  useEffect(() => {
    let cancelled = false;
    getGithubRepositories(api)
      .then(data => {
        if (!cancelled) setRepositories(data.repositories);
      })
      .catch(e => {
        if (!cancelled) setError(e.message || "Não foi possível carregar repositórios.");
      })
      .finally(() => {
        if (!cancelled) setLoadingRepos(false);
      });
    return () => { cancelled = true; };
  }, [api]);

  useEffect(() => {
    let cancelled = false;
    setFiles([]);
    setPath("");
    setReview(null);
    setAiConsent(false);
    setAiAnalysis(null);
    setListNote("");
    if (!repo) return () => { cancelled = true; };
    setLoadingFiles(true);
    setError("");
    listSourceFiles(api, repo)
      .then(data => {
        if (cancelled) return;
        setFiles(data.files);
        setListNote(data.truncated
          ? "Mostrando os primeiros 200 arquivos elegíveis. O restante não aparece nesta versão."
          : "Somente arquivos de código públicos com até 32 KB.");
      })
      .catch(e => {
        if (!cancelled) setError(e.message || "Não foi possível listar arquivos.");
      })
      .finally(() => {
        if (!cancelled) setLoadingFiles(false);
      });
    return () => { cancelled = true; };
  }, [api, repo]);

  async function inspect() {
    if (!repo || !path || loadingReview) return;
    setReview(null);
    setAiConsent(false);
    setAiAnalysis(null);
    setError("");
    setLoadingReview(true);
    try {
      const data = await reviewSelectedSource(api, repo, path);
      setReview(data);
    } catch (e) {
      setError(e.message || "Não foi possível revisar o arquivo.");
    } finally {
      setLoadingReview(false);
    }
  }

  async function analyzeWithAI() {
    if (!review || !aiConsent || aiLoading || loadingReview) return;
    setError("");
    setAiAnalysis(null);
    setAiLoading(true);
    try {
      const result = await requestAIReview(api, repo, path, review.sha, true);
      setAiAnalysis(result);
      setAiConsent(false);
    } catch (e) {
      setError(e.message || "Não foi possível obter a revisão com IA.");
    } finally {
      setAiLoading(false);
    }
  }

  const aiAvailableForFile = Boolean(review &&
    /^[a-fA-F0-9]{40}$/.test(review.sha || "") && review.content.length <= 12000);

  return <section className="github-panel code-review-panel">
    <header className="github-head">
      <div>
        <h2><Code2 size={20} aria-hidden="true"/> Revisão de código</h2>
        <p>Selecione um repositório e um arquivo público para receber sugestões de revisão.</p>
      </div>
    </header>
    <div className="code-review-controls">
      <label htmlFor="codax-review-repo">Repositório público</label>
      <select id="codax-review-repo" value={repo} disabled={loadingRepos || aiLoading} onChange={e => { setRepo(e.target.value); setAiConsent(false); setAiAnalysis(null); setError(""); }}>
        <option value="">{loadingRepos ? "Carregando..." : "Selecione um repositório"}</option>
        {repositories.map(item => <option value={item.name} key={item.name}>{item.name}</option>)}
      </select>
      <label htmlFor="codax-review-file">Arquivo de código</label>
      <select id="codax-review-file" value={path} disabled={!repo || loadingFiles || aiLoading} onChange={e => { setPath(e.target.value); setReview(null); setAiConsent(false); setAiAnalysis(null); setError(""); }}>
        <option value="">{loadingFiles ? "Listando..." : "Selecione um arquivo"}</option>
        {files.map(item => <option key={item.path} value={item.path}>{item.path}</option>)}
      </select>
      <p className="github-note">{listNote || "A leitura de conteúdo ocorre somente ao clicar em Revisar arquivo."}</p>
      <button type="button" className="code-review-run" disabled={!repo || !path || loadingReview || loadingFiles} onClick={inspect}>
        <SearchCheck size={17} aria-hidden="true"/> {loadingReview ? "Revisando..." : "Revisar arquivo selecionado"}
      </button>
    </div>
    {error && <p className="github-error" role="alert">{error} Se estiver usando acesso remoto, autorize a sessão na aba Assistente.</p>}
    {review && <div className="code-review-results">
      <h3><FileCode2 size={18} aria-hidden="true"/> {review.path}</h3>
      <p className="github-note">Revisão heurística local, sem IA externa, execução de código ou alteração de arquivos.</p>
      <h4>Observações da revisão ({review.review.findings.length})</h4>
      {review.review.findings.length === 0
        ? <p className="github-note">Nenhum padrão conhecido foi identificado. Isso não significa que o arquivo esteja livre de problemas.</p>
        : <ol className="review-findings">
            {review.review.findings.map((item, index) =>
              <li key={index}><strong>Linha {item.line} — {item.title}</strong>
                <p>{item.suggestion}</p></li>)}
          </ol>}
      {review.review.findings_truncated && <p className="github-note">A visualização mostra no máximo 20 observações.</p>}
      <div className="ai-code-review">
        <h4>Análise aprofundada opcional com IA</h4>
        <p className="github-note">A revisão local acima é gratuita. A análise com IA envia o conteúdo deste arquivo público à API externa da OpenAI e <strong>pode gerar custos adicionais de API</strong>, não cobertos pela assinatura do ChatGPT. O código não será alterado.</p>
        {!aiAvailableForFile && <p className="github-note">A revisão com IA requer um arquivo com identificador de versão e no máximo 12 mil caracteres. A revisão local continua disponível.</p>}
        <label className="ai-consent">
          <input type="checkbox" checked={aiConsent} disabled={!aiAvailableForFile || aiLoading} onChange={e => setAiConsent(e.target.checked)}/>
          Li o arquivo selecionado e autorizo seu envio à OpenAI para uma única análise.
        </label>
        <button type="button" className="code-review-run" disabled={!aiConsent || !aiAvailableForFile || aiLoading} onClick={analyzeWithAI}>
          {aiLoading ? "Consultando IA..." : "Solicitar análise com IA"}
        </button>
        {aiAnalysis && <section className="ai-analysis-result" aria-label="Recomendações da IA">
          <h4>Recomendações — somente leitura</h4>
          <pre>{aiAnalysis.analysis}</pre>
          <p className="github-note">{aiAnalysis.disclaimer}</p>
        </section>}
      </div>
      <h4>Conteúdo do arquivo (somente leitura)</h4>
      <pre className="code-review-source"><code>{review.content}</code></pre>
      <p className="github-note">{review.review.disclaimer}</p>
    </div>}
    <p className="github-note">Não são analisados arquivos privados, grandes, binários ou com nomes que indicam credenciais. A revisão local não faz commits nem chamadas pagas. A análise opcional com IA só ocorre após autorização expressa, pode gerar custos de API e nunca aplica mudanças automaticamente.</p>
  </section>;
}

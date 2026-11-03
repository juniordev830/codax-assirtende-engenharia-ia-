import { useEffect, useState } from "react";
import { FileDiff, GitPullRequest, ShieldCheck } from "lucide-react";
import { getGithubRepositories } from "./githubApi.mjs";
import { listSourceFiles, reviewSelectedSource } from "./codeReviewApi.mjs";
import { reviewBatch, requestDiffProposal } from "./multiReviewApi.mjs";

export default function MultiReviewPanel({ api }) {
  const [repos, setRepos] = useState([]);
  const [repo, setRepo] = useState("");
  const [files, setFiles] = useState([]);
  const [paths, setPaths] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingRepos, setLoadingRepos] = useState(true);
  const [error, setError] = useState("");
  const [localResult, setLocalResult] = useState(null);
  const [proposal, setProposal] = useState(null);
  const [consent, setConsent] = useState(false);

  useEffect(() => {
    let active = true;
    getGithubRepositories(api)
      .then(data => { if (active) setRepos(data.repositories); })
      .catch(e => { if (active) setError(e.message || "Falha ao consultar repositórios."); })
      .finally(() => { if (active) setLoadingRepos(false); });
    return () => { active = false; };
  }, [api]);

  useEffect(() => {
    let active = true;
    setFiles([]);
    setPaths([]);
    setLocalResult(null);
    setProposal(null);
    setConsent(false);
    if (!repo) return () => { active = false; };
    setLoading(true);
    setError("");
    listSourceFiles(api, repo)
      .then(data => { if (active) setFiles(data.files); })
      .catch(e => { if (active) setError(e.message || "Falha ao consultar arquivos."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [api, repo]);

  function toggleFile(path) {
    setPaths(current => current.includes(path) ? current.filter(item => item !== path) :
      current.length < 3 ? [...current, path] : current);
    setLocalResult(null);
    setProposal(null);
    setConsent(false);
  }

  async function runLocal() {
    if (loading || !repo || !paths.length) return;
    setError("");
    setProposal(null);
    setLocalResult(null);
    setConsent(false);
    setLoading(true);
    try {
      // User chooses the paths; every selected file is opened before analysis.
      const previews = await Promise.all(paths.map(path => reviewSelectedSource(api, repo, path)));
      const selected = previews.map(item => ({ path: item.path, expected_sha: item.sha }));
      const result = await reviewBatch(api, repo, selected);
      setLocalResult(result);
    } catch (e) {
      setError(e.message || "Não foi possível revisar os arquivos.");
    } finally {
      setLoading(false);
    }
  }

  async function propose() {
    if (loading || !consent || !localResult) return;
    setError("");
    setProposal(null);
    setLoading(true);
    try {
      const selected = localResult.files.map(file => ({ path: file.path, expected_sha: file.sha }));
      const result = await requestDiffProposal(api, repo, selected, true);
      setProposal(result);
      setConsent(false);
    } catch (e) {
      setError(e.message || "Não foi possível gerar uma proposta.");
    } finally {
      setLoading(false);
    }
  }

  const canRequestAI = Boolean(localResult && localResult.files.length <= 3 &&
    localResult.files.every(f => /^[a-fA-F0-9]{40}$/.test(f.sha || "")) &&
    localResult.files.reduce((sum, f) => sum + f.content.length, 0) <= 12000);

  return <section className="github-panel multi-review-panel">
    <header className="github-head">
      <div>
        <h2><FileDiff size={20} aria-hidden="true"/> Revisão de múltiplos arquivos</h2>
        <p>Compare até três arquivos públicos de um projeto. A IA apenas propõe um diff; nada será aplicado.</p>
      </div>
    </header>
    <div className="code-review-controls">
      <label htmlFor="multi-review-repo">Repositório público</label>
      <select id="multi-review-repo" value={repo} disabled={loadingRepos || loading}
        onChange={e => { setRepo(e.target.value); setError(""); }}>
        <option value="">{loadingRepos ? "Carregando projetos..." : "Selecione um repositório"}</option>
        {repos.map(item => <option key={item.name} value={item.name}>{item.name}</option>)}
      </select>
      <p className="github-note">Escolha de um a três arquivos. São permitidos somente arquivos públicos de código com até 32 KB cada.</p>
      <div className="multi-file-list" aria-label="Arquivos selecionáveis">
        {files.map(item => <label key={item.path} className="multi-file-item">
          <input type="checkbox" checked={paths.includes(item.path)}
            disabled={loading || (!paths.includes(item.path) && paths.length >= 3)}
            onChange={() => toggleFile(item.path)}/>
          <span>{item.path}</span><small>{item.size} bytes</small>
        </label>)}
      </div>
      <button type="button" className="code-review-run" disabled={loading || !paths.length} onClick={runLocal}>
        {loading && !localResult ? "Revisando..." : "Revisar seleção localmente"}
      </button>
    </div>
    {error && <p className="github-error" role="alert">{error} Para acesso remoto, autorize a sessão na aba Assistente.</p>}
    {localResult && <section className="multi-review-results">
      <h3><ShieldCheck size={18} aria-hidden="true"/> Revisão local — {localResult.file_count} arquivo(s)</h3>
      <p className="github-note">O conteúdo abaixo foi buscado dos repositórios públicos e não foi enviado à IA externa. Leia antes de autorizar uma proposta.</p>
      {localResult.files.map(file => <article className="github-details" key={file.path}>
        <h4>{file.path}</h4>
        <p>{file.review.findings.length} observações heurísticas</p>
        <ul className="review-findings">
          {file.review.findings.map((item, index) => <li key={index}>
            Linha {item.line} — <strong>{item.title}</strong>: {item.suggestion}
          </li>)}
        </ul>
        <pre className="code-review-source"><code>{file.content}</code></pre>
      </article>)}
      <div className="ai-code-review">
        <h4>Gerar proposta de correção com IA</h4>
        <p className="github-note">Ao confirmar, o conteúdo completo dos arquivos selecionados será enviado à OpenAI. A API pode cobrar por uso, separadamente do ChatGPT. O Codax não aplica nenhuma mudança nem executa testes.</p>
        {!canRequestAI && <p className="github-note">Para usar IA, os arquivos devem ter versão válida e totalizar no máximo 12 mil caracteres. A revisão local continua disponível.</p>}
        <label className="ai-consent">
          <input type="checkbox" disabled={loading || !canRequestAI} checked={consent} onChange={e => setConsent(e.target.checked)}/>
          Examinei os arquivos e autorizo este envio à OpenAI para gerar uma prévia de diff, sem aplicação automática.
        </label>
        <button type="button" className="code-review-run" disabled={!canRequestAI || !consent || loading} onClick={propose}>
          <GitPullRequest size={17} aria-hidden="true"/> {loading ? "Solicitando..." : "Gerar proposta de diff"}
        </button>
      </div>
    </section>}
    {proposal && <section className="multi-review-results" aria-label="Prévia de alterações proposta pela IA">
      <h3>Proposta de alterações — somente visualização</h3>
      <p>{proposal.summary}</p>
      {!proposal.proposals.length && <p className="github-note">A IA não sugeriu alterações para os arquivos selecionados.</p>}
      {proposal.proposals.map(item => <article className="github-details" key={item.path}>
        <h4>{item.path}</h4>
        <p>{item.reason}</p>
        <pre className="code-review-source"><code>{item.diff}</code></pre>
      </article>)}
      <p className="github-note">{proposal.disclaimer} Para aplicar algo, revise e implemente em uma branch separada; nenhuma mudança é feita por este módulo.</p>
    </section>}
    <p className="github-note">As análises não acessam repositórios privados, não executam comandos e não gravam código no histórico do chat.</p>
  </section>;
}

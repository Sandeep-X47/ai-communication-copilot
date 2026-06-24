import { useEffect, useState } from "react";
import { api } from "../api";

/**
 * One generator UI, configured per feature. Keeps the five module screens
 * consistent and DRY instead of five near-identical copies.
 *
 * props:
 *  - eyebrow, title, placeholder, inputLabel
 *  - optionKey: which option list drives the selector ("tones" | "reply_modes" | "dating_modes")
 *  - selectLabel: label above the selector
 *  - usePersona: show the persona dropdown
 *  - onGenerate: (inputText, choice, persona) => Promise<response>
 */
export default function Generator({
  eyebrow, title, placeholder, inputLabel = "Your message",
  optionKey, selectLabel, usePersona = false, onGenerate,
}) {
  const [text, setText] = useState("");
  const [choices, setChoices] = useState([]);
  const [choice, setChoice] = useState("");
  const [personas, setPersonas] = useState([]);
  const [persona, setPersona] = useState("default");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    api.options().then((o) => {
      if (optionKey && o[optionKey]) {
        setChoices(o[optionKey]);
        setChoice(o[optionKey][0]);
      }
      if (usePersona && o.personas) setPersonas(o.personas);
    }).catch(() => {});
  }, [optionKey, usePersona]);

  async function run() {
    if (!text.trim()) return;
    setError(""); setBusy(true); setResult(null);
    try {
      const res = await onGenerate(text, choice, usePersona ? persona : undefined);
      setResult(res);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function copy() {
    await navigator.clipboard.writeText(result.output_text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <div>
      <p className="eyebrow">{eyebrow}</p>
      <h1 className="title" style={{ fontSize: 34 }}>{title}</h1>

      <div className="card">
        <label className="label">{inputLabel}</label>
        <textarea value={text} onChange={(e) => setText(e.target.value)} placeholder={placeholder} />

        {choices.length > 0 && (
          <>
            <label className="label" style={{ marginTop: 18 }}>{selectLabel}</label>
            <div className="tone-grid">
              {choices.map((c) => (
                <button key={c} className={`tone-pill ${choice === c ? "active" : ""}`}
                        onClick={() => setChoice(c)}>{c.replace(/_/g, " ")}</button>
              ))}
            </div>
          </>
        )}

        {usePersona && personas.length > 0 && (
          <>
            <label className="label" style={{ marginTop: 18 }}>Persona</label>
            <select className="persona-select" value={persona} onChange={(e) => setPersona(e.target.value)}>
              {personas.map((p) => (
                <option key={p} value={p}>{p.replace(/_/g, " ")}</option>
              ))}
            </select>
          </>
        )}

        <button className="primary-btn" onClick={run} disabled={busy || !text.trim()}>
          {busy ? <span className="spinner" /> : "Generate"}
        </button>
        {error && <div className="error">{error}</div>}
      </div>

      {result && (
        <div className="result">
          <label className="label">
            {result.tone.replace(/_/g, " ")}
            {result.cached ? " · cached" : ""}
            {result.latency_ms ? ` · ${result.latency_ms}ms` : ""}
          </label>
          <p className="result-text">{result.output_text}</p>
          <div className="result-actions">
            <button className="chip" onClick={copy}>{copied ? "Copied ✓" : "Copy"}</button>
            <button className="chip" onClick={run}>Regenerate</button>
          </div>
        </div>
      )}
    </div>
  );
}

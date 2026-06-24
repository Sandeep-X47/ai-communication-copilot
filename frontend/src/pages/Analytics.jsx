import { useEffect, useState } from "react";
import { api } from "../api";

export default function Analytics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.analytics().then(setData).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="empty">Loading…</div>;
  if (!data) return <div className="empty">No analytics yet.</div>;

  const maxTone = Math.max(1, ...data.most_used_tones.map((t) => t.count));

  return (
    <div>
      <p className="eyebrow">Analytics</p>
      <h1 className="title" style={{ fontSize: 34 }}>Your usage.</h1>

      <div className="stat-row">
        <div className="stat"><div className="stat-num">{data.total_requests}</div><div className="stat-label">Total requests</div></div>
        <div className="stat"><div className="stat-num">{data.avg_latency_ms}<span className="stat-unit">ms</span></div><div className="stat-label">Avg latency</div></div>
        <div className="stat"><div className="stat-num">{data.cache_hits}</div><div className="stat-label">Cache hits</div></div>
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <label className="label">Most used tones</label>
        {data.most_used_tones.length === 0 ? (
          <p className="note">No data yet — generate something first.</p>
        ) : (
          data.most_used_tones.map((t) => (
            <div key={t.tone} className="bar-row">
              <span className="bar-label">{t.tone.replace(/_/g, " ")}</span>
              <span className="bar-track"><span className="bar-fill" style={{ width: `${(t.count / maxTone) * 100}%` }} /></span>
              <span className="bar-count">{t.count}</span>
            </div>
          ))
        )}
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <label className="label">By module</label>
        <div className="tone-grid">
          {data.by_module.map((m) => (
            <span key={m.mode} className="chip">{m.mode}: {m.count}</span>
          ))}
        </div>
      </div>

      <p className="note">Cache backend: {data.cache_backend}</p>
    </div>
  );
}

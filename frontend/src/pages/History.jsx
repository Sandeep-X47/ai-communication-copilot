import { useEffect, useState } from "react";
import { api } from "../api";

export default function History() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  function load() {
    api.history().then(setItems).finally(() => setLoading(false));
  }
  useEffect(load, []);

  async function remove(id) {
    await api.deleteHistory(id);
    setItems((prev) => prev.filter((i) => i.id !== id));
  }

  if (loading) return <div className="empty">Loading…</div>;

  return (
    <div>
      <p className="eyebrow">History</p>
      <h1 className="title" style={{ fontSize: 34 }}>Everything you've sent.</h1>

      {items.length === 0 ? (
        <div className="empty">No rewrites yet. Head to Rewrite and make your first one.</div>
      ) : (
        items.map((item) => (
          <div key={item.id} className="hist-item">
            <div className="hist-meta">
              <span className="hist-tone">{item.tone}</span>
              <button className="hist-del" onClick={() => remove(item.id)}>Delete</button>
            </div>
            <p className="hist-in">{item.input_text}</p>
            <p className="hist-out">{item.output_text}</p>
          </div>
        ))
      )}
    </div>
  );
}

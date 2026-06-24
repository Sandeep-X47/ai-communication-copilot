import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth";

export default function Login() {
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit() {
    setError("");
    setBusy(true);
    try {
      if (mode === "login") await login(email, password);
      else await register(email, password);
      navigate("/");
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-wrap">
      <p className="eyebrow">{mode === "login" ? "Welcome back" : "Create account"}</p>
      <h1 className="title" style={{ fontSize: 32, marginBottom: 24 }}>
        {mode === "login" ? "Sign in." : "Get started."}
      </h1>
      <div className="auth-card">
        <div className="field">
          <label className="label">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            onKeyDown={(e) => e.key === "Enter" && submit()}
          />
        </div>
        <div className="field">
          <label className="label">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="At least 6 characters"
            onKeyDown={(e) => e.key === "Enter" && submit()}
          />
        </div>
        <button className="primary-btn" onClick={submit} disabled={busy || !email || !password}>
          {busy ? <span className="spinner" /> : mode === "login" ? "Sign in" : "Create account"}
        </button>
        {error && <div className="error">{error}</div>}
        <div className="auth-toggle">
          {mode === "login" ? "No account yet? " : "Already have an account? "}
          <button onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(""); }}>
            {mode === "login" ? "Create one" : "Sign in"}
          </button>
        </div>
      </div>
    </div>
  );
}

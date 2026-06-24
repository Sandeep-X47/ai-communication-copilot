import { NavLink, Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { useAuth } from "./auth";
import Login from "./pages/Login";
import Home from "./pages/Home";
import Rewrite from "./pages/Rewrite";
import Reply from "./pages/Reply";
import Email from "./pages/Email";
import LinkedIn from "./pages/LinkedIn";
import Dating from "./pages/Dating";
import History from "./pages/History";
import Analytics from "./pages/Analytics";

const NAV = [
  ["/rewrite", "Rewrite"], ["/reply", "Reply"], ["/email", "Email"],
  ["/linkedin", "LinkedIn"], ["/dating", "Dating"],
  ["/history", "History"], ["/analytics", "Analytics"],
];

function Topbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  return (
    <div className="topbar">
      <NavLink to="/" className="brand" style={{ textDecoration: "none" }}>
        <span className="dot" /> Copilot
      </NavLink>
      {user && (
        <div className="navlinks">
          {NAV.map(([to, label]) => (
            <NavLink key={to} to={to} className="navlink">{label}</NavLink>
          ))}
          <button className="ghost-btn" onClick={() => { logout(); navigate("/login"); }}>Sign out</button>
        </div>
      )}
    </div>
  );
}

function Protected({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="empty">Loading…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  const { user, loading } = useAuth();
  const P = (el) => <Protected>{el}</Protected>;
  return (
    <div className="shell">
      <Topbar />
      <Routes>
        <Route path="/login" element={user && !loading ? <Navigate to="/" replace /> : <Login />} />
        <Route path="/" element={P(<Home />)} />
        <Route path="/rewrite" element={P(<Rewrite />)} />
        <Route path="/reply" element={P(<Reply />)} />
        <Route path="/email" element={P(<Email />)} />
        <Route path="/linkedin" element={P(<LinkedIn />)} />
        <Route path="/dating" element={P(<Dating />)} />
        <Route path="/history" element={P(<History />)} />
        <Route path="/analytics" element={P(<Analytics />)} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}

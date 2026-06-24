import { Link } from "react-router-dom";

const TILES = [
  { to: "/rewrite", title: "Rewrite", desc: "Shift any message into 8 tones, with personas." },
  { to: "/reply", title: "Reply", desc: "Turn an incoming message into a ready reply." },
  { to: "/email", title: "Email", desc: "Draft a full email from a one-line purpose." },
  { to: "/linkedin", title: "LinkedIn", desc: "Networking and referral outreach that lands." },
  { to: "/dating", title: "Dating", desc: "Friendly, respectful openers and replies." },
  { to: "/analytics", title: "Analytics", desc: "Most-used tones, latency, and cache hits." },
];

export default function Home() {
  return (
    <div>
      <p className="eyebrow">AI Communication Copilot</p>
      <h1 className="title">Say it again,<br />in the right tone.</h1>
      <p className="subtitle">
        Paste a message, pick a voice and a persona, get it back the way you meant it —
        across rewriting, replies, email, LinkedIn, and dating.
      </p>
      <div className="tiles">
        {TILES.map((t) => (
          <Link key={t.to} to={t.to} className="tile">
            <span className="tag">Live</span>
            <h3>{t.title}</h3>
            <p>{t.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}

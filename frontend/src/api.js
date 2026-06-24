// Thin API client. All network + auth-header logic lives here.
const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

function getToken() {
  return localStorage.getItem("token");
}

async function request(path, { method = "GET", body, auth = true, form = false } = {}) {
  const headers = {};
  if (auth && getToken()) headers["Authorization"] = `Bearer ${getToken()}`;

  let payload;
  if (form) {
    headers["Content-Type"] = "application/x-www-form-urlencoded";
    payload = new URLSearchParams(body).toString();
  } else if (body) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }

  const res = await fetch(`${BASE}${path}`, { method, headers, body: payload });
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      if (data.detail && typeof data.detail === "string") detail = data.detail;
    } catch (_) {}
    throw new Error(detail);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  register: (email, password) =>
    request("/auth/register", { method: "POST", body: { email, password }, auth: false }),
  login: (email, password) =>
    request("/auth/login", { method: "POST", body: { username: email, password }, auth: false, form: true }),
  me: () => request("/auth/me"),

  options: () => request("/options", { auth: false }),

  rewrite: (text, tone, persona) => request("/rewrite", { method: "POST", body: { text, tone, persona } }),
  reply: (message, mode, persona) => request("/reply", { method: "POST", body: { message, mode, persona } }),
  email: (purpose, tone, persona) => request("/email", { method: "POST", body: { purpose, tone, persona } }),
  linkedin: (intent, persona) => request("/linkedin", { method: "POST", body: { intent, persona } }),
  dating: (message, mode) => request("/dating", { method: "POST", body: { message, mode } }),

  history: () => request("/history"),
  deleteHistory: (id) => request(`/history/${id}`, { method: "DELETE" }),
  analytics: () => request("/analytics"),
};

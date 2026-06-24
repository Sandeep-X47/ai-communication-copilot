import Generator from "../components/Generator";
import { api } from "../api";

export default function Reply() {
  return (
    <Generator
      eyebrow="Reply" title="Answer in one tap."
      inputLabel="Incoming message" placeholder="Can we schedule a meeting tomorrow?"
      optionKey="reply_modes" selectLabel="Reply type" usePersona
      onGenerate={(msg, mode, persona) => api.reply(msg, mode, persona)}
    />
  );
}

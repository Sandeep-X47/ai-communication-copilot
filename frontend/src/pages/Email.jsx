import Generator from "../components/Generator";
import { api } from "../api";

export default function Email() {
  return (
    <Generator
      eyebrow="Email" title="From a line to a letter."
      inputLabel="What's it about?" placeholder="Need leave tomorrow"
      optionKey="tones" selectLabel="Tone" usePersona
      onGenerate={(purpose, tone, persona) => api.email(purpose, tone, persona)}
    />
  );
}

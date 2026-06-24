import Generator from "../components/Generator";
import { api } from "../api";

export default function Rewrite() {
  return (
    <Generator
      eyebrow="Rewrite" title="Tune the voice."
      inputLabel="Your message" placeholder="send report by eod"
      optionKey="tones" selectLabel="Tone" usePersona
      onGenerate={(text, tone, persona) => api.rewrite(text, tone, persona)}
    />
  );
}

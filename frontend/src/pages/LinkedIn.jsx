import Generator from "../components/Generator";
import { api } from "../api";

export default function LinkedIn() {
  return (
    <Generator
      eyebrow="LinkedIn" title="Outreach that gets replies."
      inputLabel="Your intent" placeholder="Need a referral for an SDE role at..."
      usePersona
      onGenerate={(intent, _choice, persona) => api.linkedin(intent, persona)}
    />
  );
}

import Generator from "../components/Generator";
import { api } from "../api";

export default function Dating() {
  return (
    <Generator
      eyebrow="Dating" title="Break the ice, stay yourself."
      inputLabel="Context or their message" placeholder="Hey — saw you're into climbing too"
      optionKey="dating_modes" selectLabel="Vibe"
      onGenerate={(msg, mode) => api.dating(msg, mode)}
    />
  );
}

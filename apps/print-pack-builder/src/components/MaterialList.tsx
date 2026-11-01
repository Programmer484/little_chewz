import type { ResolvedMaterial } from "../../shared/types.ts";

/** Materials an activity prints, with plain-language availability. */
export function MaterialList({ materials }: { materials: ResolvedMaterial[] }) {
  if (!materials.length) return null;
  return (
    <ul className="materials">
      {materials.map((m) => (
        <li key={m.resourceId} className={m.resource.available ? "" : "unavailable"}>
          <span className="material-title">{m.resource.title}</span>
          {m.note && <span className="material-note"> · {m.note}</span>}
          {!m.resource.available && <span className="material-flag"> · Not available yet: {m.resource.reason}</span>}
        </li>
      ))}
    </ul>
  );
}

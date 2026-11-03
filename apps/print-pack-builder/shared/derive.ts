/**
 * Read a lesson's print options straight from its Teacher Guide source
 * (lesson.json) and the resource catalogue (catalog/resources.json).
 *
 * A link is printable when the catalogue says its `type` is `student_material`.
 * Where it appears in the guide decides how the teacher sees it:
 *
 * | lesson.json                                   | Print Pack Builder                     |
 * | --------------------------------------------- | -------------------------------------- |
 * | GIVE row in a step                            | included automatically                 |
 * | MORE row in a step                            | checkbox                               |
 * | step.options (A, B, C...)                     | choose one                             |
 * | GIVE row inside an option                     | printed when that option is chosen     |
 * | MORE row inside an option                     | checkbox shown when that option is chosen |
 * | Preparation `core`, not used in any step      | included automatically                 |
 * | `optional_prep` / `bonuses`, not used in a step | checkbox under "Extras"              |
 *
 * Copy rules come only from each worksheet link's explicit quantity.\n * Multi-card sheets are defined in catalog/resources.json.\n */
import type { ExtensionSpec, LessonManifest, MaterialSpec, OptionSpec, QuantityRule, SectionSpec } from "./types.ts";

export interface RegistryEntry {
  title: string;
  type?: string;
  print?: { cards_per_sheet?: number };
}
export type RegistryLike = Record<string, RegistryEntry>;

interface LinkRef {
  ref?: string;
  description?: string;
  quantity?: QuantityRule;
}
interface Row extends LinkRef {
  kind?: string;
  links?: LinkRef[];
}
interface LessonStep {
  id: number | string;
  title: string;
  rows?: Row[];
  options?: { label: string; title: string; group_size?: number; rows?: Row[] }[];
}
/** The parts of a lesson.json this app reads. */
export interface LessonSource {
  core?: LinkRef[];
  optional_prep?: LinkRef[];
  bonuses?: LinkRef[];
  steps?: LessonStep[];
}

export const PRINTABLE_TYPE = "student_material";

const clean = (text?: string) => text?.replace(/^\s*[—–-]\s*/, "").trim() || undefined;

function links(row: Row): LinkRef[] {
  const out: LinkRef[] = [];
  if (row.ref) out.push({ ref: row.ref, description: row.description, quantity: row.quantity });
  for (const link of row.links ?? []) if (link.ref) out.push(link);
  return out;
}

const slug = (value: string | number) =>
  String(value)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "") || "x";

export interface LessonInput {
  questId: string;
  /** Lesson folder, e.g. "02-secret-ingredients". */
  folder: string;
  title: string;
  order: number;
  /** Parsed lesson.json, or null when the lesson has no Teacher Guide source yet. */
  source: LessonSource | null;
}

/** Stable URL-safe ID: quest + folder without its number, e.g. ccc-q01-secret-ingredients. */
export function lessonIdFor(questId: string, folder: string): string {
  return `${questId}-${folder.replace(/^\d+-/, "")}`;
}

export function deriveManifest(input: LessonInput, registry: RegistryLike): LessonManifest {
  const base = {
    lessonId: lessonIdFor(input.questId, input.folder),
    questId: input.questId,
    order: input.order,
    title: input.title,
  };
  if (!input.source)
    return {
      ...base,
      status: "in_progress",
      statusNote: "The Teacher Guide for this lesson isn't ready yet, so there's nothing to print.",
      sections: [],
    };

  const lesson = input.source;
  const isStudent = (ref?: string): ref is string =>
    Boolean(ref && Object.hasOwn(registry, ref) && registry[ref].type === PRINTABLE_TYPE);
  const prepText = new Map<string, string>();
  for (const item of [...(lesson.core ?? []), ...(lesson.optional_prep ?? []), ...(lesson.bonuses ?? [])])
    if (item.ref && item.description && !prepText.has(item.ref)) prepText.set(item.ref, clean(item.description)!);

  const material = (link: LinkRef): MaterialSpec => {
    const ref = link.ref!;
    const note = prepText.get(ref) ?? clean(link.description);
    const cards = registry[ref].print?.cards_per_sheet;
    if (link.quantity !== "per_student" && link.quantity !== "per_group")
      throw new Error(`Worksheet ${ref} requires quantity: per_student or per_group in lesson.json`);
    return {
      resourceId: ref,
      rule: link.quantity,
      ...(cards ? { cardsPerSheet: cards } : {}),
      ...(note ? { note } : {}),
    };
  };
  const extension = (id: string, link: LinkRef): ExtensionSpec => ({
    id,
    title: registry[link.ref!].title,
    ...(clean(link.description) ? { summary: clean(link.description) } : {}),
    materials: [material(link)],
  });

  const sections: SectionSpec[] = [];
  const mentioned = new Set<string>(); // refs used anywhere in the Teaching Flow

  for (const step of lesson.steps ?? []) {
    const stepId = `step-${slug(step.id)}`;
    const stepTitle = `Step ${step.id} · ${step.title}`;
    const core: MaterialSpec[] = [];
    const optional: ExtensionSpec[] = [];
    for (const row of step.rows ?? [])
      for (const link of links(row).filter((l) => isStudent(l.ref))) {
        mentioned.add(link.ref!);
        if (row.kind === "GIVE") core.push(material(link));
        else if (row.kind === "MORE") optional.push(extension(`${stepId}-more-${link.ref}`, link));
      }
    if (core.length) sections.push({ kind: "core", id: stepId, title: stepTitle, materials: core });
    if (optional.length) sections.push({ kind: "optional", id: `${stepId}-more`, title: stepTitle, items: optional });

    if (step.options?.length) {
      const options: OptionSpec[] = step.options.map((option) => {
        const optionId = `${stepId}-${slug(option.label)}`;
        const materials: MaterialSpec[] = [];
        const extensions: ExtensionSpec[] = [];
        for (const row of option.rows ?? [])
          for (const link of links(row).filter((l) => isStudent(l.ref))) {
            mentioned.add(link.ref!);
            if (row.kind === "MORE") extensions.push(extension(`${optionId}-more-${link.ref}`, link));
            else materials.push(material(link));
          }
        return {
          id: optionId,
          label: option.label,
          title: option.title,
          ...(option.group_size ? { groupSize: option.group_size } : {}),
          ...(materials.length || extensions.length ? {} : { summary: "Nothing to print." }),
          materials,
          extensions,
        };
      });
      if (options.some((o) => o.materials.length || o.extensions?.length))
        sections.push({ kind: "choice", id: `${stepId}-choice`, title: stepTitle, options });
    }
  }

  // Preparation core stays mandatory unless already covered by an unconditional GIVE.
  const unconditional = new Set((lesson.steps ?? []).flatMap((step) => (step.rows ?? [])
    .filter((row) => row.kind === "GIVE").flatMap(links).map((link) => `${link.ref}:${link.quantity}`)));
  const prepOnly = (lesson.core ?? []).filter((c) => isStudent(c.ref) && !unconditional.has(`${c.ref}:${c.quantity}`));
  if (prepOnly.length)
    sections.unshift({ kind: "core", id: "preparation", title: "Preparation", materials: prepOnly.map(material) });
  // Optional preparation and bonus worksheets not used in the flow become extras.
  const seen = new Set([...mentioned, ...prepOnly.map((c) => c.ref!)]);
  const extras: ExtensionSpec[] = [];
  for (const item of [...(lesson.optional_prep ?? []), ...(lesson.bonuses ?? [])])
    if (isStudent(item.ref) && !seen.has(item.ref)) {
      seen.add(item.ref);
      extras.push(extension(`extras-${item.ref}`, item));
    }
  if (extras.length) sections.push({ kind: "optional", id: "extras", title: "Extras", items: extras });

  const anyMaterial = sections.length > 0;
  return {
    ...base,
    status: anyMaterial ? "ready" : "no_student_printing",
    ...(anyMaterial ? {} : { statusNote: "This lesson's Teacher Guide has no student worksheets to print." }),
    sections,
  };
}

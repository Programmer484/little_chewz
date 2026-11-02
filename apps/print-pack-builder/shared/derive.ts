/**
 * Read a lesson's print options straight from its Teacher Guide source
 * (lesson.json) and the resource catalogue (catalog/resources.json).
 *
 * A link is printable when the catalogue says its `type` is `student_worksheet`.
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
 * Default copies come from the guide's description ("group" -> one per group,
 * "class" -> one for the class, otherwise one per student); teachers can
 * change every number. Cards printed several to a page come from the
 * catalogue's print.cards_per_sheet.
 */
import type { ExtensionSpec, LessonManifest, MaterialSpec, OptionSpec, QuantityRule, SectionSpec } from "./types.ts";

export interface RegistryEntry {
  title: string;
  type?: string;
  status?: string;
  print?: { cards_per_sheet?: number };
}
export type RegistryLike = Record<string, RegistryEntry>;

interface LinkRef {
  ref?: string;
  description?: string;
}
interface Row extends LinkRef {
  kind?: string;
  links?: LinkRef[];
}
interface LessonStep {
  id: number | string;
  title: string;
  rows?: Row[];
  options?: { label: string; title: string; rows?: Row[] }[];
}
/** The parts of a lesson.json this app reads. */
export interface LessonSource {
  core?: LinkRef[];
  optional_prep?: LinkRef[];
  bonuses?: LinkRef[];
  steps?: LessonStep[];
}

export const PRINTABLE_TYPE = "student_worksheet";

/** Default copy rule from the guide's own wording. */
export function ruleFromText(text: string): QuantityRule {
  if (/\bgroups?\b|\bteams?\b/i.test(text) && !/\bper student\b/i.test(text)) return "per_group";
  if (/\b(per|for the|one per) class\b|\bclassroom display\b|\bteacher copy\b/i.test(text)) return "per_class";
  return "per_student";
}

const clean = (text?: string) => text?.replace(/^\s*[—–-]\s*/, "").trim() || undefined;

function links(row: Row): LinkRef[] {
  const out: LinkRef[] = [];
  if (row.ref) out.push({ ref: row.ref, description: row.description });
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
  const coreRefs = new Set((lesson.core ?? []).map((c) => c.ref).filter(isStudent));

  const material = (link: LinkRef): MaterialSpec => {
    const ref = link.ref!;
    const note = prepText.get(ref) ?? clean(link.description);
    const cards = registry[ref].print?.cards_per_sheet;
    return {
      resourceId: ref,
      rule: ruleFromText([prepText.get(ref), clean(link.description)].filter(Boolean).join(" ")),
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
  const placed = new Set<string>(); // refs already included automatically
  const mentioned = new Set<string>(); // refs used anywhere in the Teaching Flow

  for (const step of lesson.steps ?? []) {
    const stepId = `step-${slug(step.id)}`;
    const stepTitle = `Step ${step.id} · ${step.title}`;
    const core: MaterialSpec[] = [];
    const optional: ExtensionSpec[] = [];
    for (const row of step.rows ?? [])
      for (const link of links(row).filter((l) => isStudent(l.ref))) {
        mentioned.add(link.ref!);
        const always = row.kind === "GIVE" || coreRefs.has(link.ref!);
        if (always && !placed.has(link.ref!)) {
          core.push(material(link));
          placed.add(link.ref!);
        } else if (row.kind === "MORE" && !placed.has(link.ref!))
          optional.push(extension(`${stepId}-more-${link.ref}`, link));
      }
    if (core.length) sections.push({ kind: "core", id: stepId, title: stepTitle, materials: core });
    if (optional.length) sections.push({ kind: "optional", id: `${stepId}-more`, title: `${stepTitle} · Optional`, items: optional });

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
          ...(materials.length || extensions.length ? {} : { summary: "Nothing to print." }),
          materials,
          extensions,
        };
      });
      if (options.some((o) => o.materials.length || o.extensions?.length))
        sections.push({ kind: "choice", id: `${stepId}-choice`, title: stepTitle, options });
    }
  }

  // Preparation "core" worksheets the Teaching Flow never links still print for everyone.
  const prepOnly = (lesson.core ?? []).filter((c) => isStudent(c.ref) && !mentioned.has(c.ref!) && !placed.has(c.ref!));
  if (prepOnly.length) {
    prepOnly.forEach((c) => placed.add(c.ref!));
    sections.unshift({ kind: "core", id: "preparation", title: "Preparation", materials: prepOnly.map(material) });
  }
  // Optional preparation and bonus worksheets not used in the flow become extras.
  const seen = new Set([...mentioned, ...placed]);
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

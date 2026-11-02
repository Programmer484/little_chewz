import { DEFAULT_GROUP_SIZE, DEFAULT_STUDENT_COUNT } from "./limits.ts";
import type {
  ClientResource,
  ExtensionSpec,
  LessonManifest,
  MaterialSpec,
  QuestInfo,
  ResolvedExtension,
  ResolvedLesson,
  ResolvedMaterial,
  ResolvedSection,
} from "./types.ts";

const RULES = new Set(["per_student", "per_group"]);
const ID = /^[a-z0-9][a-z0-9-]*$/;

/** Every material in a manifest, in manifest order. */
export function allMaterials(manifest: LessonManifest): MaterialSpec[] {
  const out: MaterialSpec[] = [];
  for (const section of manifest.sections) {
    if (section.kind === "core") out.push(...section.materials);
    if (section.kind === "choice")
      for (const option of section.options) {
        out.push(...option.materials);
        for (const ext of option.extensions ?? []) out.push(...ext.materials);
      }
    if (section.kind === "optional") for (const item of section.items) out.push(...item.materials);
  }
  return out;
}

/**
 * Objective checks for a print manifest. Returns human-readable problems;
 * an empty list means the manifest is usable.
 */
export function validateManifest(
  manifest: LessonManifest,
  knownResourceIds: ReadonlySet<string>,
  knownQuestIds: ReadonlySet<string>,
): string[] {
  const p: string[] = [];
  const where = manifest.lessonId || "(missing lessonId)";
  if (!ID.test(manifest.lessonId ?? "")) p.push(`${where}: lessonId must be lowercase kebab-case`);
  if (!knownQuestIds.has(manifest.questId)) p.push(`${where}: unknown questId ${manifest.questId}`);
  if (!manifest.title) p.push(`${where}: title is required`);
  if (!["ready", "no_student_printing", "in_progress"].includes(manifest.status))
    p.push(`${where}: invalid status ${manifest.status}`);
  if (!Array.isArray(manifest.sections)) {
    p.push(`${where}: sections must be an array`);
    return p;
  }
  if (manifest.status !== "ready" && allMaterials(manifest).length > 0)
    p.push(`${where}: only a "ready" lesson may list materials`);
  if (manifest.status === "ready" && allMaterials(manifest).length === 0)
    p.push(`${where}: a "ready" lesson needs at least one material`);

  const ids = new Set<string>();
  const claim = (id: string, what: string) => {
    if (!ID.test(id ?? "")) p.push(`${where}: ${what} id "${id}" must be lowercase kebab-case`);
    if (ids.has(id)) p.push(`${where}: duplicate id "${id}"`);
    ids.add(id);
  };
  const perResource = new Map<string, MaterialSpec>();
  const checkMaterial = (m: MaterialSpec) => {
    if (!knownResourceIds.has(m.resourceId)) p.push(`${where}: unknown resourceId ${m.resourceId}`);
    if (!RULES.has(m.rule)) p.push(`${where}: ${m.resourceId} has an invalid quantity rule`);
    if (m.cardsPerSheet !== undefined && !(Number.isInteger(m.cardsPerSheet) && m.cardsPerSheet >= 1))
      p.push(`${where}: ${m.resourceId} cardsPerSheet must be a positive whole number`);
    const prior = perResource.get(m.resourceId);
    if (prior && prior.cardsPerSheet !== m.cardsPerSheet)
      p.push(`${where}: ${m.resourceId} has inconsistent cardsPerSheet between placements`);
    perResource.set(m.resourceId, m);
  };
  const checkExtension = (e: ExtensionSpec) => {
    claim(e.id, "extension");
    if (!e.title) p.push(`${where}: extension ${e.id} needs a title`);
    if (!e.materials?.length) p.push(`${where}: extension ${e.id} needs at least one material`);
    e.materials?.forEach(checkMaterial);
  };

  for (const s of manifest.sections) {
    claim(s.id, "section");
    if (!s.title) p.push(`${where}: section ${s.id} needs a title`);
    if (s.kind === "core") s.materials.forEach(checkMaterial);
    else if (s.kind === "choice") {
      if (s.options.length < 2) p.push(`${where}: choice ${s.id} needs at least two options`);
      for (const o of s.options) {
        claim(o.id, "option");
        if (!o.label || !o.title) p.push(`${where}: option ${o.id} needs a label and title`);
        o.materials.forEach(checkMaterial);
        (o.extensions ?? []).forEach(checkExtension);
      }
    } else if (s.kind === "optional") s.items.forEach(checkExtension);
    else p.push(`${where}: unknown section kind ${(s as { kind: string }).kind}`);
  }
  return p;
}

/**
 * Attach sanitized resource details (title, availability) to a manifest.
 * `describe` must never return Drive IDs or URLs.
 */
export function resolveLesson(
  manifest: LessonManifest,
  quests: ReadonlyMap<string, QuestInfo>,
  describe: (resourceId: string) => ClientResource,
  extra: { demo?: boolean } = {},
): ResolvedLesson {
  const material = (m: MaterialSpec): ResolvedMaterial => ({ ...m, resource: describe(m.resourceId) });
  const extension = (e: ExtensionSpec): ResolvedExtension => ({ ...e, materials: e.materials.map(material) });
  const sections: ResolvedSection[] = manifest.sections.map((s) => {
    if (s.kind === "core") return { ...s, materials: s.materials.map(material) };
    if (s.kind === "choice")
      return {
        ...s,
        options: s.options.map((o) => ({
          ...o,
          materials: o.materials.map(material),
          extensions: (o.extensions ?? []).map(extension),
        })),
      };
    return { ...s, items: s.items.map(extension) };
  });
  const lesson: ResolvedLesson = {
    lessonId: manifest.lessonId,
    questId: manifest.questId,
    questTitle: quests.get(manifest.questId)?.title ?? manifest.questId,
    order: manifest.order,
    title: manifest.title,
    status: manifest.status,
    statusNote: manifest.statusNote,
    defaults: {
      studentCount: manifest.defaults?.studentCount ?? DEFAULT_STUDENT_COUNT,
      groupSize: manifest.defaults?.groupSize ?? DEFAULT_GROUP_SIZE,
    },
    sections,
    printable: false,
    ...(extra.demo ? { demo: true } : {}),
  };
  lesson.printable =
    manifest.status === "ready" && resolvedMaterials(lesson).some((m) => m.resource.available);
  return lesson;
}

export function resolvedMaterials(lesson: ResolvedLesson): ResolvedMaterial[] {
  const out: ResolvedMaterial[] = [];
  for (const s of lesson.sections) {
    if (s.kind === "core") out.push(...s.materials);
    if (s.kind === "choice")
      for (const o of s.options) {
        out.push(...o.materials);
        for (const e of o.extensions) out.push(...e.materials);
      }
    if (s.kind === "optional") for (const i of s.items) out.push(...i.materials);
  }
  return out;
}

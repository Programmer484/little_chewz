/**
 * Server-side catalogue. Builds every lesson from the repository's own records:
 *
 *   catalog/quests.json -> each quest.json -> learning_sequence -> lessons/<folder>/lesson.json
 *
 * and resolves which worksheets may be downloaded. A worksheet is downloadable
 * when a lesson.json links it, the catalogue types it `student_material`, its
 * published_url names a valid official Drive file. A staged draft does not
 * hide the existing official version. There is no
 * separate allowlist. Drive file IDs stay here; the browser only receives
 * sanitized lessons.
 */
import { deriveManifest, PRINTABLE_TYPE, type LessonSource, type RegistryEntry } from "../shared/derive.ts";
import { allMaterials, resolveLesson } from "../shared/manifest.ts";
import type { AllowedMime, ClientResource, LessonManifest, QuestInfo, ResolvedLesson, ResourceMode } from "../shared/types.ts";

/** The subset of a catalog/resources.json record this app reads. */
export interface RegistryRecord extends RegistryEntry {
  published_url?: string | null;
}
export type Registry = Record<string, RegistryRecord>;

export interface QuestIndex {
  school_index: { quest_manifest: string }[];
}
interface QuestFile {
  id: string;
  quest_number?: number;
  title: string;
  learning_sequence: { folder: string; title: string }[];
}

export interface DemoResource {
  title: string;
  fixture: string;
  mimeType: AllowedMime;
}

export type ServedSource = { kind: "drive"; fileId: string } | { kind: "demo-fixture"; fixture: string; mimeType: AllowedMime } | { kind: "demo-placeholder" };

export interface ServedResource {
  id: string;
  title: string;
  source: ServedSource;
}

const DRIVE_FILE = /\/file\/d\/([A-Za-z0-9_-]{10,})(?:[/?#]|$)/;

export function driveFileId(url: string | null | undefined): string | null {
  const m = url ? DRIVE_FILE.exec(url) : null;
  return m ? m[1] : null;
}

/** Trusted Drive file ID for a printable resource, or the reason it cannot be downloaded. */
export function trustedDriveFile(record: RegistryRecord | undefined): { fileId: string } | { problem: string } {
  if (!record) return { problem: "not in catalog/resources.json" };
  if (record.type !== PRINTABLE_TYPE) return { problem: `type ${record.type} is not a student material` };
  // A live official worksheet stays downloadable even when a new draft is pending.
  // Publication state is derived, never read from a stored status field.
  const id = driveFileId(record.published_url);
  if (!id) return { problem: "published_url is not a Drive file URL" };
  return { fileId: id };
}

export interface CatalogInput {
  registry: Registry;
  questIndex: QuestIndex;
  /** Repository files by repo-relative path: quest.json and lesson.json files. */
  files: Record<string, unknown>;
  demo: { lesson: LessonManifest; quest: QuestInfo; resources: Record<string, DemoResource> };
}

export function parseMode(value: string | undefined): ResourceMode {
  return value === "demo" || value === "drive" ? value : "disabled";
}

const dirname = (path: string) => path.slice(0, path.lastIndexOf("/"));

/** Shared path resolution for both production and CI's revision comparison. */
export const lessonSourcePath = (questManifestPath: string, lessonFolder: string) =>
  `${dirname(questManifestPath)}/lessons/${lessonFolder}/lesson.json`;

/** Every lesson in every quest, derived from its Teacher Guide source. */
export function deriveLessons(input: Pick<CatalogInput, "registry" | "questIndex" | "files">) {
  const quests: QuestInfo[] = [];
  const manifests: LessonManifest[] = [];
  input.questIndex.school_index.forEach((entry, questOrder) => {
    const quest = input.files[entry.quest_manifest] as QuestFile | undefined;
    if (!quest) throw new Error(`Missing quest file ${entry.quest_manifest}`);
    quests.push({ id: quest.id, title: `Quest ${quest.quest_number ?? questOrder + 1}: ${quest.title}`, order: questOrder });
    quest.learning_sequence.forEach((lesson, order) => {
      const path = lessonSourcePath(entry.quest_manifest, lesson.folder);
      const source = (input.files[path] as LessonSource | undefined) ?? null;
      manifests.push(deriveManifest({ questId: quest.id, folder: lesson.folder, title: lesson.title, order, source }, input.registry));
    });
  });
  return { quests, manifests };
}

export function createCatalog(input: CatalogInput) {
  const { quests: questList, manifests } = deriveLessons(input);
  const quests = new Map(questList.map((q) => [q.id, q]));
  quests.set(input.demo.quest.id, input.demo.quest);
  const has = <T extends object>(o: T, k: string) => Object.hasOwn(o, k);

  /** Worksheets linked from a lesson that can be downloaded, with their trusted Drive file. */
  const real = new Map<string, { title: string; fileId: string }>();
  const problems = new Map<string, string>();
  for (const id of new Set(manifests.flatMap(allMaterials).map((m) => m.resourceId))) {
    const result = trustedDriveFile(has(input.registry, id) ? input.registry[id] : undefined);
    if ("fileId" in result) real.set(id, { title: input.registry[id].title, fileId: result.fileId });
    else problems.set(id, result.problem);
  }

  function describe(id: string, mode: ResourceMode): ClientResource {
    const title = has(input.registry, id) ? input.registry[id].title : id;
    if (!real.has(id)) return { id, title, available: false, reason: "Coming soon: not published yet." };
    if (mode === "disabled") return { id, title, available: false, reason: "Worksheet downloads are switched off on this site." };
    return { id, title, available: true };
  }

  function lessons(mode: ResourceMode): ResolvedLesson[] {
    const out = manifests
      .map((m) => resolveLesson(m, quests, (id) => describe(id, mode)))
      .sort((a, b) => (quests.get(a.questId)?.order ?? 0) - (quests.get(b.questId)?.order ?? 0) || a.order - b.order);
    if (mode === "demo")
      out.unshift(
        resolveLesson(
          input.demo.lesson,
          quests,
          (id) => {
            const r = has(input.demo.resources, id) ? input.demo.resources[id] : undefined;
            return r ? { id, title: r.title, available: true } : { id, title: id, available: false, reason: "Unknown demo file." };
          },
          { demo: true },
        ),
      );
    return out;
  }

  /** What the Worker may serve for an ID in a mode; null means refuse. */
  function lookup(id: string, mode: ResourceMode): ServedResource | null {
    if (mode === "demo") {
      const d = has(input.demo.resources, id) ? input.demo.resources[id] : undefined;
      if (d) return { id, title: d.title, source: { kind: "demo-fixture", fixture: d.fixture, mimeType: d.mimeType } };
      const r = real.get(id);
      // Demo mode never contacts Google: real worksheets become labelled placeholder pages.
      return r ? { id, title: r.title, source: { kind: "demo-placeholder" } } : null;
    }
    if (mode === "drive") {
      const r = real.get(id);
      return r ? { id, title: r.title, source: { kind: "drive", fileId: r.fileId } } : null;
    }
    return null;
  }

  return { lessons, lookup, describe, manifests, notDownloadable: problems };
}

export type Catalog = ReturnType<typeof createCatalog>;

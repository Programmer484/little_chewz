/**
 * Server-side catalogue: joins the lesson print manifests, the canonical
 * resource registry (catalog/resources.json) and the pilot allowlist.
 * Drive file IDs stay here; the browser only receives sanitized lessons.
 */
import { resolveLesson } from "../shared/manifest.ts";
import type {
  AllowedMime,
  ClientResource,
  LessonManifest,
  PilotAllowEntry,
  QuestInfo,
  ResolvedLesson,
  ResourceMode,
} from "../shared/types.ts";

/** The subset of a catalog/resources.json record this app reads. */
export interface RegistryRecord {
  title: string;
  type?: string;
  status?: string;
  published_url?: string | null;
  holding_url?: string | null;
  publication?: { verification?: string; drive_file_id?: string };
}
export type Registry = Record<string, RegistryRecord>;

export interface DemoResource {
  title: string;
  fixture: string;
  mimeType: AllowedMime;
}

export type ServedSource =
  | { kind: "drive"; fileId: string }
  | { kind: "demo-fixture"; fixture: string }
  | { kind: "demo-placeholder"; pages: number };

export interface ServedResource {
  id: string;
  title: string;
  mimeType: AllowedMime;
  source: ServedSource;
}

/** Registry types that may be printed for students. */
const PRINTABLE_TYPES = new Set(["student_worksheet", "visual_asset"]);
const DRIVE_FILE = /\/file\/d\/([A-Za-z0-9_-]{10,})(?:[/?#]|$)/;

export function driveFileId(url: string | null | undefined): string | null {
  const m = url ? DRIVE_FILE.exec(url) : null;
  return m ? m[1] : null;
}

/** Trusted Drive file ID for an allowlisted resource, or the reason it is not servable. */
export function trustedDriveFile(
  record: RegistryRecord | undefined,
  entry: PilotAllowEntry,
): { fileId: string } | { problem: string } {
  if (!record) return { problem: "not in catalog/resources.json" };
  if (!PRINTABLE_TYPES.has(record.type ?? "")) return { problem: `type ${record.type} is not a printable student resource` };
  if (entry.source === "published") {
    if (record.status !== "published") return { problem: `status is ${record.status}, not published` };
    if (record.publication?.verification !== "verified") return { problem: "publication is not verified" };
    const id = driveFileId(record.published_url);
    if (!id) return { problem: "published_url is not a Drive file URL" };
    if (record.publication.drive_file_id && record.publication.drive_file_id !== id)
      return { problem: "published_url does not match publication.drive_file_id" };
    return { fileId: id };
  }
  if (entry.source === "holding") {
    if (!entry.approval?.trim()) return { problem: "holding source needs an explicit pilot approval note" };
    const id = driveFileId(record.holding_url);
    return id ? { fileId: id } : { problem: "holding_url is not a Drive file URL" };
  }
  return { problem: "unknown allowlist source" };
}

export interface CatalogInput {
  registry: Registry;
  allowlist: Record<string, PilotAllowEntry>;
  manifests: LessonManifest[];
  quests: QuestInfo[];
  demo: { lesson: LessonManifest; quest: QuestInfo; resources: Record<string, DemoResource> };
}

export function parseMode(value: string | undefined): ResourceMode {
  return value === "demo" || value === "drive" ? value : "disabled";
}

export function createCatalog(input: CatalogInput) {
  const quests = new Map(input.quests.map((q) => [q.id, q]));
  quests.set(input.demo.quest.id, input.demo.quest);
  const pagesFor = new Map<string, number>();
  for (const m of input.manifests)
    for (const s of m.sections) {
      const mats =
        s.kind === "core"
          ? s.materials
          : s.kind === "choice"
            ? s.options.flatMap((o) => [...o.materials, ...(o.extensions ?? []).flatMap((e) => e.materials)])
            : s.items.flatMap((i) => i.materials);
      for (const mat of mats) if (mat.pages) pagesFor.set(mat.resourceId, mat.pages);
    }

  /** Allowlisted real resources that pass every registry check. */
  const real = new Map<string, { title: string; mimeType: AllowedMime; fileId: string }>();
  const problems = new Map<string, string>();
  for (const [id, entry] of Object.entries(input.allowlist)) {
    const result = trustedDriveFile(Object.hasOwn(input.registry, id) ? input.registry[id] : undefined, entry);
    if ("fileId" in result) real.set(id, { title: input.registry[id].title, mimeType: entry.mimeType, fileId: result.fileId });
    else problems.set(id, result.problem);
  }

  function describe(id: string, mode: ResourceMode): ClientResource {
    const known = Object.hasOwn(input.registry, id);
    const title = known ? input.registry[id].title : id;
    if (!known) return { id, title, available: false, reason: "Not found in the resource catalogue." };
    if (!Object.hasOwn(input.allowlist, id)) return { id, title, available: false, reason: "Awaiting review for the pilot." };
    if (!real.has(id)) return { id, title, available: false, reason: "Not published and verified yet." };
    if (mode === "disabled")
      return { id, title, available: false, reason: "Worksheet downloads are not switched on for this site yet." };
    return { id, title, available: true };
  }

  function lessons(mode: ResourceMode): ResolvedLesson[] {
    const out = input.manifests
      .map((m) => resolveLesson(m, quests, (id) => describe(id, mode)))
      .sort((a, b) => (quests.get(a.questId)?.order ?? 0) - (quests.get(b.questId)?.order ?? 0) || a.order - b.order);
    if (mode === "demo")
      out.unshift(
        resolveLesson(
          input.demo.lesson,
          quests,
          (id) => {
            const r = input.demo.resources[id];
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
      const d = Object.hasOwn(input.demo.resources, id) ? input.demo.resources[id] : undefined;
      if (d) return { id, title: d.title, mimeType: d.mimeType, source: { kind: "demo-fixture", fixture: d.fixture } };
      const r = real.get(id);
      // Demo mode never contacts Google: real resources become labelled placeholder pages.
      if (r) return { id, title: r.title, mimeType: "application/pdf", source: { kind: "demo-placeholder", pages: pagesFor.get(id) ?? 1 } };
      return null;
    }
    if (mode === "drive") {
      const r = real.get(id);
      return r ? { id, title: r.title, mimeType: r.mimeType, source: { kind: "drive", fileId: r.fileId } } : null;
    }
    return null;
  }

  return { lessons, lookup, describe, allowlistProblems: problems };
}

export type Catalog = ReturnType<typeof createCatalog>;

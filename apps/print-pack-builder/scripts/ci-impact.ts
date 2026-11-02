/**
 * Decide whether the full Print Pack Builder check is needed.
 *
 * For repository data edits, run the CURRENT builder implementation over both
 * Git revisions and compare exactly what its teacher API and download resolver
 * would expose. No duplicate mapping of worksheet/lesson fields lives here.
 *
 * If anything cannot be compared, fail: the workflow defaults to running checks.
 */
import { execFileSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { allMaterials } from "../shared/manifest.ts";
import { createCatalog, lessonSourcePath, type CatalogInput, type QuestIndex, type Registry } from "../worker/catalog.ts";
import type { LessonManifest } from "../shared/types.ts";

const ROOT = fileURLToPath(new URL("../../../", import.meta.url));
type Inputs = Pick<CatalogInput, "registry" | "questIndex" | "files">;
type Reader = (path: string) => unknown | null;

function git(...args: string[]): string {
  return execFileSync("git", args, { cwd: ROOT, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
}

function required<T>(reader: Reader, path: string): T {
  const value = reader(path);
  if (value === null || value === undefined) throw new Error("Missing required repository data: " + path);
  return value as T;
}

/** Use the actual quest index and source-path resolver; never enumerate lessons. */
export function loadInputs(reader: Reader): Inputs {
  const registry = required<Registry>(reader, "catalog/resources.json");
  const questIndex = required<QuestIndex>(reader, "catalog/quests.json");
  const files: Record<string, unknown> = {};

  for (const entry of questIndex.school_index) {
    const quest = required<{ learning_sequence: { folder: string }[] }>(reader, entry.quest_manifest);
    files[entry.quest_manifest] = quest;
    for (const lesson of quest.learning_sequence) {
      const path = lessonSourcePath(entry.quest_manifest, lesson.folder);
      const source = reader(path);
      if (source !== null) files[path] = source;
    }
  }
  return { registry, questIndex, files };
}

/** Mirror the app's real lesson list and resource lookup, including Drive IDs. */
export function printSurface(inputs: Inputs): string {
  // A synthetic demo entry is required by createCatalog but never included in
  // lessons("drive"). Real manifests and permissions use production code.
  const id = "ci-comparison-demo";
  const demoLesson: LessonManifest = {
    lessonId: id, questId: id, title: "Comparison sentinel",
    status: "in_progress", order: 0, sections: [],
  };
  const catalog = createCatalog({
    ...inputs,
    demo: {
      lesson: demoLesson,
      quest: { id, title: "Comparison sentinel", order: -1 },
      resources: {},
    },
  });
  const ids = [...new Set(catalog.manifests.flatMap(allMaterials).map((m) => m.resourceId))].sort();
  return JSON.stringify({
    lessons: catalog.lessons("drive"),
    downloadTargets: ids.map((resourceId) => [resourceId, catalog.lookup(resourceId, "drive")]),
  });
}

export function hasPrintImpact(previous: Inputs, proposed: Inputs): boolean {
  return printSurface(previous) !== printSurface(proposed);
}

function readAt(revision: string): Reader {
  return (path) => {
    try {
      const value = git("show", revision + ":" + path);
      return JSON.parse(value) as unknown;
    } catch (error) {
      // A missing lesson.json is valid; a malformed existing file isn't.
      try {
        git("cat-file", "-e", revision + ":" + path);
      } catch {
        return null;
      }
      throw error;
    }
  };
}

function readWorkingTree(): Reader {
  return (path) => {
    const file = resolve(ROOT, path);
    try {
      return JSON.parse(readFileSync(file, "utf8")) as unknown;
    } catch (error) {
      // Only a genuinely absent file may become a missing lesson source.
      if (!existsSync(file)) return null;
      throw error;
    }
  };
}

export function needsFullChecks(changedPaths: readonly string[], previous: Inputs, proposed: Inputs): boolean {
  if (changedPaths.some((path) =>
    path.startsWith("apps/print-pack-builder/") ||
    path === ".github/workflows/print-pack-builder.yml")) return true;
  return hasPrintImpact(previous, proposed);
}

function main() {
  const base = process.argv[2];
  if (!base || !/^[a-f0-9]{40}$/.test(base)) throw new Error("Missing or invalid base commit");
  git("rev-parse", "--verify", base + "^{commit}");
  const changedPaths = git("diff", "--name-only", "-z", base, "HEAD", "--")
    .split("\0").filter(Boolean);
  if (changedPaths.some((path) =>
    path.startsWith("apps/print-pack-builder/") ||
    path === ".github/workflows/print-pack-builder.yml")) {
    process.stdout.write("run_full=true\nreason=app-or-workflow-code-changed\n");
    return;
  }

  const previous = loadInputs(readAt(base));
  const proposed = loadInputs(readWorkingTree());
  const impacted = hasPrintImpact(previous, proposed);
  process.stdout.write("run_full=" + impacted + "\n");
  process.stdout.write("reason=" + (impacted ? "print-output-changed" : "print-output-unchanged") + "\n");
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main();

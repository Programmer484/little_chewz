/**
 * The version-controlled configuration must agree with the canonical
 * repository records: catalog/resources.json and each quest's quest.json.
 */
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import demoLesson from "../config/demo/lesson.json";
import demoResources from "../config/demo/resources.json";
import allowlist from "../config/pilot-allowlist.json";
import quests from "../config/quests.json";
import { allMaterials, validateManifest } from "../shared/manifest.ts";
import type { LessonManifest, PilotAllowEntry } from "../shared/types.ts";
import { type Registry, trustedDriveFile } from "../worker/catalog.ts";
import { MANIFESTS, catalog } from "../worker/data.ts";
import { FIXTURES } from "../worker/demo/fixtures.generated.ts";

const ROOT = resolve(__dirname, "../../..");
const readJson = (path: string) => JSON.parse(readFileSync(resolve(ROOT, path), "utf8"));
const registry: Registry = readJson("catalog/resources.json");
const questIndex: { school_index: { quest_manifest: string }[] } = readJson("catalog/quests.json");
const questFiles = questIndex.school_index.map((s) => ({ path: s.quest_manifest, data: readJson(s.quest_manifest) }));
const entries = allowlist.resources as Record<string, PilotAllowEntry>;

/** Every `ref` in a lesson.json, i.e. the resources its Teaching Flow and Preparation use. */
function refs(value: unknown): Set<string> {
  const out = new Set<string>();
  const walk = (v: unknown) => {
    if (Array.isArray(v)) v.forEach(walk);
    else if (v && typeof v === "object")
      for (const [k, x] of Object.entries(v)) {
        if (k === "ref" && typeof x === "string") out.add(x);
        else walk(x);
      }
  };
  walk(value);
  return out;
}

describe("lesson print manifests", () => {
  it("loads every manifest in config/lessons", () => {
    expect(MANIFESTS.map((m) => m.lessonId).sort()).toEqual([
      "ccc-q01-activate",
      "ccc-q01-secret-ingredients",
      "ccc-q01-set-the-table",
      "ccc-q01-the-showdown",
    ]);
  });

  it.each(MANIFESTS.map((m) => [m.lessonId, m] as const))("%s is valid against the registry", (_, manifest) => {
    expect(validateManifest(manifest, new Set(Object.keys(registry)), new Set(quests.map((q) => q.id)))).toEqual([]);
  });

  it.each(MANIFESTS.map((m) => [m.lessonId, m] as const))("%s matches its lesson in quest.json and lesson.json", (_, manifest) => {
    const quest = questFiles.find((q) => q.data.id === manifest.questId);
    expect(quest, "quest.json for questId").toBeDefined();
    const lesson = quest!.data.learning_sequence.find((l: { folder: string }) => l.folder === manifest.lessonFolder);
    expect(lesson, "learning_sequence entry").toBeDefined();
    expect(lesson.title).toBe(manifest.title);
    const lessonPath = resolve(ROOT, quest!.path, "..", "lessons", manifest.lessonFolder!, "lesson.json");
    const materials = allMaterials(manifest);
    if (materials.length) {
      const used = refs(JSON.parse(readFileSync(lessonPath, "utf8")));
      for (const m of materials) expect(used, `${m.resourceId} appears in lesson.json`).toContain(m.resourceId);
    }
  });

  it("only lists student-printable resources", () => {
    for (const m of MANIFESTS.flatMap(allMaterials)) expect(registry[m.resourceId].type).toBe("student_worksheet");
  });

  it("catches broken manifests", () => {
    const bad = {
      lessonId: "Bad Id",
      questId: "nope",
      order: 1,
      title: "",
      status: "ready",
      sections: [
        { kind: "choice", id: "c", title: "C", options: [{ id: "a", label: "A", title: "A", materials: [{ resourceId: "missing", quantity: { rule: "per_person" } }] }] },
        { kind: "core", id: "c", title: "Dup", materials: [{ resourceId: "missing", quantity: { rule: "per_class" }, cardsPerSheet: 0 }] },
      ],
    } as unknown as LessonManifest;
    const problems = validateManifest(bad, new Set(Object.keys(registry)), new Set(["ccc-q01"])).join("\n");
    for (const expected of ["kebab-case", "unknown questId", "title is required", "at least two options", "unknown resourceId missing", "invalid quantity rule", 'duplicate id "c"', "cardsPerSheet"])
      expect(problems).toContain(expected);
  });
});

describe("pilot allowlist", () => {
  it.each(Object.entries(entries))("%s resolves to a trusted, published Drive file", (id, entry) => {
    const result = trustedDriveFile(registry[id], entry);
    expect(result).toHaveProperty("fileId");
    expect(entry.approval.length).toBeGreaterThan(10);
  });

  it("has no problems and only allows resources a lesson uses", () => {
    expect([...catalog.allowlistProblems]).toEqual([]);
    const used = new Set(MANIFESTS.flatMap(allMaterials).map((m) => m.resourceId));
    for (const id of Object.keys(entries)) expect(used).toContain(id);
  });

  it("never stores Drive IDs or URLs in app configuration", () => {
    const fileIds = new Set<string>();
    for (const r of Object.values(registry))
      for (const url of [r.published_url, r.holding_url]) {
        const m = url ? /\/d\/([A-Za-z0-9_-]{10,})/.exec(url) : null;
        if (m) fileIds.add(m[1]);
      }
    expect(fileIds.size).toBeGreaterThan(5);
    const config = JSON.stringify([allowlist, MANIFESTS, quests, demoLesson, demoResources]);
    expect(config).not.toMatch(/drive\.google|docs\.google|https?:/);
    for (const id of fileIds) expect(config).not.toContain(id);
  });

  it("refuses unpublished, unverified, mismatched or non-student resources", () => {
    const pub: PilotAllowEntry = { source: "published", mimeType: "application/pdf", approval: "test" };
    expect(trustedDriveFile(registry["ccc-q01-set-the-table-kwls-starter"], pub)).toEqual({ problem: "status is unpublished, not published" });
    expect(trustedDriveFile(registry["ccc-q01-set-the-table-team-builder"], pub)).toEqual({ problem: "publication is not verified" });
    expect(trustedDriveFile(registry["ccc-q01-secret-ingredients-teacher-guide"], pub)).toHaveProperty("problem");
    expect(trustedDriveFile(undefined, pub)).toHaveProperty("problem");
    const record = { ...registry["ccc-q01-secret-ingredients-chapter-notes"], publication: { verification: "verified", drive_file_id: "someOtherFileId123" } };
    expect(trustedDriveFile(record, pub)).toEqual({ problem: "published_url does not match publication.drive_file_id" });
    expect(trustedDriveFile(registry["ccc-q01-set-the-table-kwls-starter"], { ...pub, source: "holding", approval: " " })).toHaveProperty("problem");
  });
});

describe("lesson availability", () => {
  const byId = (mode: "disabled" | "demo" | "drive") => new Map(catalog.lessons(mode).map((l) => [l.lessonId, l]));

  it("groups lessons in teaching order", () => {
    expect(catalog.lessons("drive").map((l) => l.title)).toEqual(["Activate", "Set the Table", "Secret Ingredients", "The Showdown"]);
    expect(catalog.lessons("demo")[0].lessonId).toBe("demo-sample-lesson");
  });

  it("marks what can and cannot be downloaded", () => {
    const drive = byId("drive");
    expect(drive.get("ccc-q01-activate")).toMatchObject({ status: "no_student_printing", printable: false });
    expect(drive.get("ccc-q01-the-showdown")).toMatchObject({ status: "in_progress", printable: false });
    expect(drive.get("ccc-q01-set-the-table")).toMatchObject({ status: "ready", printable: false });
    expect(drive.get("ccc-q01-secret-ingredients")).toMatchObject({ status: "ready", printable: true });
    expect(byId("disabled").get("ccc-q01-secret-ingredients")!.printable).toBe(false);
  });
});

describe("demo configuration", () => {
  it("is a valid manifest whose files all exist", () => {
    const demo = demoLesson as LessonManifest;
    expect(validateManifest(demo, new Set(Object.keys(demoResources)), new Set(["demo"]))).toEqual([]);
    for (const [id, r] of Object.entries(demoResources)) if (!id.startsWith("$")) expect(FIXTURES).toHaveProperty((r as { fixture: string }).fixture);
  });
});

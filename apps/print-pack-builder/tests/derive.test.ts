/**
 * The Print Pack Builder is derived from the Teacher Guide sources, so these
 * tests run against the real lesson.json files and catalogue as well as a
 * small synthetic guide.
 */
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import demoLesson from "../config/demo/lesson.json";
import demoResources from "../config/demo/resources.json";
import { deriveManifest, lessonIdFor, type LessonSource, type RegistryLike } from "../shared/derive.ts";
import { allMaterials, validateManifest } from "../shared/manifest.ts";
import type { LessonManifest } from "../shared/types.ts";
import { type Registry, trustedDriveFile } from "../worker/catalog.ts";
import { catalog } from "../worker/data.ts";
import { FIXTURES } from "../worker/demo/fixtures.generated.ts";

const ROOT = resolve(__dirname, "../../..");
const registry: Registry = JSON.parse(readFileSync(resolve(ROOT, "catalog/resources.json"), "utf8"));

const reg: RegistryLike = {
  sheet: { title: "Sheet", type: "student_worksheet" },
  group: { title: "Group Card", type: "student_worksheet", print: { cards_per_sheet: 4 } },
  ext: { title: "Extension", type: "student_worksheet" },
  bonus: { title: "Bonus", type: "student_worksheet" },
  prep: { title: "Prep Only", type: "student_worksheet" },
  slides: { title: "Slides", type: "slide_deck" },
  key: { title: "Answer Key", type: "teacher_companion" },
};
const guide: LessonSource = {
  core: [
    { ref: "slides", description: "Slides 1–5" },
    { ref: "prep", quantity: "per_student", description: "One per student" },
  ],
  optional_prep: [{ ref: "group", quantity: "per_group", description: "One per group of 3–4" }],
  bonuses: [{ ref: "bonus", quantity: "per_group", description: "— Word wall" }],
  steps: [
    {
      id: 1,
      title: "Hook",
      rows: [
        { kind: "SHOW", text: "Slide 1" } as never,
        { kind: "GIVE", ref: "sheet", quantity: "per_student", description: "One per student" },
        { kind: "MORE", links: [{ ref: "ext", quantity: "per_student", description: "+10 min" }, { ref: "key", description: "Teacher reference" }] },
      ],
    },
    {
      id: 2,
      title: "Choose One",
      rows: [],
      options: [
        { label: "A", title: "Cards", rows: [{ kind: "GIVE", links: [{ ref: "group", quantity: "per_group", description: "One per team" }] }] },
        { label: "B", title: "Talk", rows: [{ kind: "DO", text: "Discuss." } as never] },
      ],
    },
    { id: 3, title: "Wrap", rows: [{ kind: "ASK", text: "?" } as never] },
  ],
};

describe("deriveManifest", () => {
  const m = deriveManifest({ questId: "q1", folder: "02-test-lesson", title: "Test", order: 2, source: guide }, reg);

  it("maps the guide's structure", () => {
    expect(m.lessonId).toBe("q1-test-lesson");
    expect(m.status).toBe("ready");
    expect(validateManifest(m, new Set(Object.keys(reg)), new Set(["q1"]))).toEqual([]);
    expect(m.sections.map((s) => `${s.kind}:${s.id}`)).toEqual([
      "core:preparation",
      "core:step-1",
      "optional:step-1-more",
      "choice:step-2-choice",
      "optional:extras",
    ]);
  });

  it("includes GIVE and Preparation core worksheets, and makes MORE worksheets checkboxes", () => {
    const [prep, step1, more, choice] = m.sections;
    expect(prep).toMatchObject({ title: "Preparation", materials: [{ resourceId: "prep", rule: "per_student" }] });
    expect(step1).toMatchObject({ title: "Step 1 · Hook", materials: [{ resourceId: "sheet", rule: "per_student", note: "One per student" }] });
    expect(more).toMatchObject({ items: [{ title: "Extension", summary: "+10 min", materials: [{ resourceId: "ext" }] }] });
    if (choice.kind !== "choice") throw new Error("expected a choice");
    expect(choice.options.map((o) => o.label)).toEqual(["A", "B"]);
    expect(choice.options[0].materials).toEqual([{ resourceId: "group", rule: "per_group", cardsPerSheet: 4, note: "One per group of 3–4" }]);
    expect(choice.options[1]).toMatchObject({ summary: "Nothing to print.", materials: [] });
  });

  it("never offers slides, teacher pages or other non-student links", () => {
    const ids = allMaterials(m).map((x) => x.resourceId);
    expect(ids).not.toContain("slides");
    expect(ids).not.toContain("key");
  });

  it("offers unused optional and bonus worksheets once, under Extras", () => {
    // "group" is in optional_prep but already used in Step 2, so only "bonus" is an extra.
    expect(m.sections.at(-1)).toMatchObject({ kind: "optional", id: "extras", title: "Extras", items: [{ id: "extras-bonus", summary: "Word wall" }] });
  });

  it("handles lessons without worksheets or without a guide yet", () => {
    expect(deriveManifest({ questId: "q", folder: "00-a", title: "A", order: 0, source: { steps: [] } }, reg).status).toBe("no_student_printing");
    expect(deriveManifest({ questId: "q", folder: "03-b", title: "B", order: 0, source: null }, reg).status).toBe("in_progress");
  });

  it("keeps Preparation core mandatory even when it also appears as optional in the flow", () => {
    const source: LessonSource = {
      core: [{ ref: "sheet", quantity: "per_student", description: "One per student" }],
      steps: [{ id: 1, title: "Optional reuse", rows: [{ kind: "MORE", ref: "sheet", quantity: "per_group" }] }],
    };
    const m = deriveManifest({ questId: "q", folder: "00-test", title: "Test", order: 0, source }, reg);
    expect(m.sections.map((x) => x.kind)).toEqual(["core", "optional"]);
    expect(allMaterials(m).map((x) => x.rule)).toEqual(["per_student", "per_group"]);
  });

  it("retains separate core quantities for the same resource in different placements", () => {
    const source: LessonSource = {
      core: [{ ref: "sheet", quantity: "per_student" }],
      steps: [{ id: 1, title: "Group reuse", rows: [{ kind: "GIVE", ref: "sheet", quantity: "per_group" }] }],
    };
    const m = deriveManifest({ questId: "q", folder: "00-test", title: "Test", order: 0, source }, reg);
    expect(allMaterials(m).map((x) => x.rule)).toEqual(["per_student", "per_group"]);
  });

  it("uses explicit quantities and rejects missing metadata", () => {
    expect(lessonIdFor("ccc-q01", "02-secret-ingredients")).toBe("ccc-q01-secret-ingredients");
    const missing: LessonSource = { steps: [{ id: 1, title: "Test", rows: [{ kind: "GIVE", ref: "sheet" }] }] };
    expect(() => deriveManifest({ questId: "q", folder: "00-test", title: "Test", order: 0, source: missing }, reg))
      .toThrow(/requires quantity/);
    const invalid: LessonSource = { steps: [{ id: 1, title: "Test", rows: [{ kind: "GIVE", ref: "sheet", quantity: "per_class" as never }] }] };
    expect(() => deriveManifest({ questId: "q", folder: "00-test", title: "Test", order: 0, source: invalid }, reg))
      .toThrow(/requires quantity/);
  });
});

describe("the real Teacher Guides", () => {
  const byId = new Map(catalog.manifests.map((m) => [m.lessonId, m]));

  it("lists every lesson of the quest in teaching order", () => {
    expect(catalog.lessons("drive").map((l) => l.title)).toEqual([
      "Activate",
      "Set the Table",
      "Secret Ingredients",
      "The Showdown",
      "Chew On This",
      "Plate It Forward",
      "Celebrate",
    ]);
  });

  it("every derived lesson is a valid manifest", () => {
    for (const m of catalog.manifests) expect(validateManifest(m, new Set(Object.keys(registry)), new Set(["ccc-q01"]))).toEqual([]);
  });

  it("matches the Secret Ingredients Teaching Flow", () => {
    const si = byId.get("ccc-q01-secret-ingredients")!;
    expect(si.sections.map((s) => s.title)).toEqual([
      "Step 1 · Clue Hunt + Quick Inference",
      "Step 1 · Clue Hunt + Quick Inference · Optional",
      "Step 2 · Chapter Prediction",
      "Step 4 · Choose One Small Bite",
    ]);
    const choice = si.sections[3];
    if (choice.kind !== "choice") throw new Error("expected a choice");
    expect(choice.options.map((o) => [o.label, o.materials.map((x) => x.resourceId), (o.extensions ?? []).map((e) => e.materials[0].resourceId)])).toEqual([
      ["A", [], []],
      ["B", ["ccc-q01-secret-ingredients-character-profile-core"], ["ccc-q01-secret-ingredients-character-profile"]],
    ]);
  });

  it("marks what can and cannot be downloaded", () => {
    const lessons = new Map(catalog.lessons("drive").map((l) => [l.lessonId, l]));
    expect(lessons.get("ccc-q01-activate")).toMatchObject({ status: "no_student_printing", printable: false });
    expect(lessons.get("ccc-q01-secret-ingredients")).toMatchObject({ status: "ready", printable: true });
    expect(lessons.get("ccc-q01-set-the-table")).toMatchObject({ status: "ready", printable: true });
    expect(lessons.get("ccc-q01-celebrate")).toMatchObject({ status: "in_progress", printable: false });
    expect(catalog.lessons("disabled").some((l) => l.printable && !l.demo)).toBe(false);
  });

  it("only offers published student worksheets for download, through their catalogue Drive file", () => {
    for (const id of new Set(catalog.manifests.flatMap(allMaterials).map((m) => m.resourceId))) {
      const record = registry[id];
      expect(record.type).toBe("student_worksheet");
      const served = catalog.lookup(id, "drive");
      if (record.status === "published") expect(served?.source).toEqual({ kind: "drive", fileId: (trustedDriveFile(record) as { fileId: string }).fileId });
      else expect(served).toBeNull();
    }
  });

  it("refuses unpublished, mismatched or non-student resources", () => {
    expect(trustedDriveFile(registry["ccc-q01-set-the-table-school-song-activity"])).toEqual({ problem: "status is unpublished, not published" });
    expect(trustedDriveFile(registry["ccc-q01-set-the-table-kwls-starter"])).toMatchObject({ fileId: "1O6VRLTguA3Cb76k3U5refPd4Hiz7sBoK" });
    expect(trustedDriveFile(registry["ccc-q01-secret-ingredients-teacher-guide"])).toHaveProperty("problem");
    expect(trustedDriveFile(undefined)).toHaveProperty("problem");
    const mismatched = { ...registry["ccc-q01-secret-ingredients-chapter-notes"], publication: { drive_file_id: "someOtherFileId123" } };
    expect(trustedDriveFile(mismatched)).toEqual({ problem: "published_url does not match publication.drive_file_id" });
    expect(catalog.lookup("ccc-q01-secret-ingredients-teacher-guide", "drive")).toBeNull();
  });
});

describe("demo configuration", () => {
  it("is a valid manifest whose files all exist", () => {
    expect(validateManifest(demoLesson as LessonManifest, new Set(Object.keys(demoResources)), new Set(["demo"]))).toEqual([]);
    for (const [id, r] of Object.entries(demoResources)) if (!id.startsWith("$")) expect(FIXTURES).toHaveProperty((r as { fixture: string }).fixture);
  });
});

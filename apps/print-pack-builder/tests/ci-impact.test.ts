import { describe, expect, it } from "vitest";
import { hasPrintImpact, loadInputs, needsFullChecks } from "../scripts/ci-impact.ts";
import { lessonSourcePath, type CatalogInput } from "../worker/catalog.ts";

const QUEST = "content/demo/quest.json";
const LESSON = lessonSourcePath(QUEST, "01-example");
const FILE = "1ZG0ZO1l-ExsskVsKh-s9IYh3YBvO81XP";
type Inputs = Pick<CatalogInput, "registry" | "questIndex" | "files">;

function fixture(): Inputs {
  return {
    questIndex: { school_index: [{ quest_manifest: QUEST }] },
    registry: {
      sheet: {
        title: "Student sheet",
        type: "student_worksheet",
        published_url: "https://drive.google.com/file/d/" + FILE + "/view",
        publication: { drive_file_id: FILE },
      },
      other: { title: "Unreferenced teacher file", type: "teacher_companion" },
    },
    files: {
      [QUEST]: {
        id: "q-test",
        title: "Quest",
        learning_sequence: [{ folder: "01-example", title: "Lesson" }],
      },
      [LESSON]: {
        steps: [{ id: 1, title: "Activity", rows: [
          { kind: "GIVE", ref: "sheet", quantity: "per_student", description: "One per student" },
          { kind: "DO", text: "Explain the activity." },
        ] }],
      },
    },
  };
}

function changed(edit: (input: Inputs) => void): boolean {
  const before = fixture();
  const after = structuredClone(before);
  edit(after);
  return hasPrintImpact(before, after);
}

function lesson(input: Inputs): {
  steps: { title: string; rows: { kind: string; ref?: string; quantity?: string; description?: string; text?: string }[] }[];
} {
  return input.files[LESSON] as ReturnType<typeof lesson>;
}

describe("semantic Print Pack CI impact", () => {
  it("ignores non-print teaching text", () => {
    expect(changed((input) => { lesson(input).steps[0].rows[1].text = "Different instructions."; })).toBe(false);
  });

  it("ignores harmless source formatting and unreferenced catalog changes", () => {
    expect(changed((input) => { input.registry.other.title = "Updated teacher-only document"; })).toBe(false);
  });

  it("detects worksheet moves from GIVE to MORE without changing the link", () => {
    expect(changed((input) => { lesson(input).steps[0].rows[0].kind = "MORE"; })).toBe(true);
  });

  it("detects explicit quantity and visible notes independently", () => {
    expect(changed((input) => { lesson(input).steps[0].rows[0].quantity = "per_group"; })).toBe(true);
    expect(changed((input) => { lesson(input).steps[0].rows[0].description = "For a small team"; })).toBe(true);
  });

  it("detects visible step title changes", () => {
    expect(changed((input) => { lesson(input).steps[0].title = "Different activity"; })).toBe(true);
  });

  it("detects worksheet display-name and print setting changes", () => {
    expect(changed((input) => { input.registry.sheet.title = "New worksheet title"; })).toBe(true);
    expect(changed((input) => { input.registry.sheet.print = { cards_per_sheet: 3 }; })).toBe(true);
    expect(changed((input) => {
      lesson(input).steps[0].rows[0].kind = "MORE";
      input.registry.sheet.title = "New worksheet title";
    })).toBe(true);
  });

  it("detects published download URL changes even when printable options look identical", () => {
    expect(changed((input) => {
      input.registry.sheet.published_url =
        "https://drive.google.com/file/d/1qY77-jKnCFBoj-MI2su-o48jKRcwzRiZ/view";
      input.registry.sheet.publication = { drive_file_id: "1qY77-jKnCFBoj-MI2su-o48jKRcwzRiZ" };
    })).toBe(true);
  });

  it("detects resource type and official-link availability changes", () => {
    expect(changed((input) => { input.registry.sheet.type = "teacher_companion"; })).toBe(true);
    expect(changed((input) => { input.registry.sheet.published_url = null; })).toBe(true);
  });

  it("detects quest navigation and lesson availability changes", () => {
    expect(changed((input) => {
      (input.files[QUEST] as { title: string }).title = "A renamed quest";
    })).toBe(true);
    expect(changed((input) => { delete input.files[LESSON]; })).toBe(true);
  });

  it("uses the current production source-path resolver", () => {
    const original = fixture();
    const docs = new Map<string, unknown>([
      ["catalog/resources.json", original.registry],
      ["catalog/quests.json", original.questIndex],
      ...Object.entries(original.files),
    ]);
    expect(hasPrintImpact(loadInputs((path) => docs.get(path) ?? null), original)).toBe(false);
  });

  it("always checks Print Pack code changes even if data is identical", () => {
    const input = fixture();
    expect(needsFullChecks(["apps/print-pack-builder/shared/derive.ts"], input, input)).toBe(true);
    expect(needsFullChecks([".github/workflows/print-pack-builder.yml"], input, input)).toBe(true);
    expect(needsFullChecks(["content/demo/lessons/01-example/lesson.json"], input, input)).toBe(false);
  });
});

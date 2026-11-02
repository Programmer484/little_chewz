import { describe, expect, it } from "vitest";
import { computePlan, copiesFor, groupCount, printSequence, quantityProblems } from "../shared/plan.ts";
import { testLesson } from "./helpers.ts";

const q = { studentCount: 25, groupSize: 4 };
const pick = (plan: ReturnType<typeof computePlan>, id: string, rule?: string) =>
  plan.lines.find((l) => l.resourceId === id && (!rule || l.rule === rule))!;
const ids = (plan: ReturnType<typeof computePlan>) => plan.lines.map((l) => l.resourceId);

describe("class quantities", () => {
  it("rounds groups up, including incomplete groups", () => {
    expect(groupCount(17, 4)).toBe(5);
    expect(groupCount(17, 17)).toBe(1);
    expect(groupCount(1, 4)).toBe(1);
  });

  it("counts physical sheets for multi-card cutouts", () => {
    expect(copiesFor(5, 4)).toBe(2);
    expect(copiesFor(8, 4)).toBe(2);
    expect(copiesFor(9)).toBe(9);
  });

  it("validates class size, group sizes and overrides", () => {
    expect(quantityProblems({ studentCount: 0, groupSize: 4 })).toHaveLength(1);
    expect(quantityProblems({ studentCount: 25.5, groupSize: 4 })).toHaveLength(1);
    expect(quantityProblems({ studentCount: 25, groupSize: 0 })).toHaveLength(1);
    expect(quantityProblems({ ...q, groupSizes: { a: 0 } })).toHaveLength(1);
    expect(quantityProblems({ ...q, groupSizes: { a: 201 } })).toHaveLength(1);
    expect(quantityProblems({ ...q, copies: { a: -1 } })).toHaveLength(1);
    expect(quantityProblems({ ...q, copies: { a: 501 } })).toHaveLength(1);
    expect(quantityProblems({ ...q, copies: { a: 0 } })).toEqual([]);
  });
});

describe("Guided Printing (default)", () => {
  it("always includes mandatory core and requires a selection in each A/B group", () => {
    const plan = computePlan(testLesson(), { choices: {}, extensions: {} }, q);
    expect(plan.problems).toContain("Choose one option for “Small Bite”.");
    expect(ids(plan)).toEqual(["core-sheet"]);
    expect(plan.lines[0].copies).toBe(25);
  });

  it("permits exactly the chosen activity and its checked extension", () => {
    const chosen = computePlan(testLesson(), { choices: { bite: "b" }, extensions: { "b-extra": true } }, q);
    expect(ids(chosen)).toEqual(["core-sheet", "team-cards", "b-extra-sheet"]);
    expect(chosen.problems).toEqual([]);
    const ignored = computePlan(testLesson(), { choices: { bite: "a" }, extensions: { "b-extra": true } }, q);
    expect(ids(ignored)).toEqual(["core-sheet", "song-sheet"]);
  });
});

describe("Custom Printing", () => {
  it("unlocks required worksheets and permits both alternatives simultaneously", () => {
    const plan = computePlan(testLesson(), {
      customize: true, choices: {}, extensions: {},
      materials: { "core:core-sheet": false },
      customChoices: { a: true, b: true },
    }, q);
    expect(plan.problems).toEqual([]);
    expect(ids(plan)).toEqual(["song-sheet", "team-cards"]);
  });

  it("lets teachers remove individual worksheets within an option", () => {
    const plan = computePlan(testLesson(), {
      customize: true, choices: {}, extensions: {},
      customChoices: { a: true, b: true }, materials: { "a:song-sheet": false },
    }, q);
    expect(ids(plan)).toEqual(["core-sheet", "team-cards"]);
  });

  it("allows no A/B selection when core remains, but rejects an entirely empty pack", () => {
    const kept = computePlan(testLesson(), { customize: true, choices: {}, extensions: {} }, q);
    expect(ids(kept)).toEqual(["core-sheet"]);
    expect(kept.problems).toEqual([]);
    const empty = computePlan(testLesson(), {
      customize: true, choices: {}, extensions: {}, materials: { "core:core-sheet": false },
    }, q);
    expect(empty.lines).toEqual([]);
    expect(empty.problems).toEqual(["Select at least one worksheet."]);
  });

  it("does not apply Custom selections after returning to Guided mode", () => {
    const plan = computePlan(testLesson(), {
      customize: false, choices: { bite: "a" }, extensions: {},
      customChoices: { a: false, b: true }, materials: { "core:core-sheet": false },
    }, q);
    expect(ids(plan)).toEqual(["core-sheet", "song-sheet"]);
  });
});

describe("per-activity quantities", () => {
  it("uses an independent editable group size for every selected activity", () => {
    const plan = computePlan(testLesson(), {
      choices: { bite: "b" }, extensions: { "group-sheet": true },
    }, {
      studentCount: 17, groupSize: 4,
      groupSizes: { b: 5, "group-sheet": 3 },
    });
    expect(pick(plan, "team-cards")).toMatchObject({ groupSize: 5, needed: 4, defaultCopies: 1 });
    expect(pick(plan, "group-sheet")).toMatchObject({ groupSize: 3, needed: 6, defaultCopies: 6 });
  });

  it("treats a whole class as one large group", () => {
    const plan = computePlan(testLesson(),
      { choices: { bite: "c" }, extensions: { poster: true } },
      { studentCount: 17, groupSize: 4, groupSizes: { poster: 17 } });
    expect(pick(plan, "poster")).toMatchObject({ needed: 1, copies: 1 });
  });

  it("keeps the same resource separate when selected with different quantity rules", () => {
    const plan = computePlan(testLesson(),
      { choices: { bite: "c" }, extensions: { reuse: true } }, q);
    expect(ids(plan)).toEqual(["core-sheet", "core-sheet"]);
    expect(pick(plan, "core-sheet", "per_student")).toMatchObject({ copies: 25 });
    expect(pick(plan, "core-sheet", "per_group")).toMatchObject({ copies: 7 });
  });

  it("keeps teacher copy overrides without changing defaults", () => {
    const plan = computePlan(testLesson(), { choices: { bite: "b" }, extensions: {} },
      { ...q, copies: { "core-sheet:per_student": 30, "team-cards:per_group:b": 3 } });
    expect(pick(plan, "core-sheet")).toMatchObject({ defaultCopies: 25, copies: 30, edited: true });
    expect(pick(plan, "team-cards")).toMatchObject({ defaultCopies: 2, copies: 3, edited: true });
  });

  it("shows unavailable materials but excludes them from downloaded pages", () => {
    const plan = computePlan(testLesson(),
      { choices: { bite: "c" }, extensions: { locked: true } }, q);
    expect(ids(plan)).not.toContain("locked-sheet");
    expect(plan.unavailable).toMatchObject([{ resourceId: "locked-sheet" }]);
  });
});

describe("one fixed print sequence", () => {
  it("makes consecutive packets then shared copies grouped by resource", () => {
    const plan = computePlan(testLesson(),
      { choices: { bite: "b" }, extensions: { "b-extra": true, poster: true } },
      { studentCount: 3, groupSize: 2, copies: { "b-extra-sheet:per_student": 2 }, groupSizes: { poster: 3 } });
    expect(printSequence(plan.lines)).toEqual({
      packets: [["core-sheet", "b-extra-sheet"], ["core-sheet", "b-extra-sheet"], ["core-sheet"]],
      shared: [
        { resourceId: "team-cards", frontOnly: true },
        { resourceId: "poster", frontOnly: false },
      ],
    });
  });
});

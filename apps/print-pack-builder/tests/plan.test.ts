import { describe, expect, it } from "vitest";
import { computePlan, copiesFor, groupCount, printSequence, quantityProblems } from "../shared/plan.ts";
import { testLesson } from "./helpers.ts";

const q = { studentCount: 25, groupSize: 4 };
const ids = (plan: ReturnType<typeof computePlan>) => plan.lines.map((l) => l.resourceId);
const line = (plan: ReturnType<typeof computePlan>, id: string) => plan.lines.find((l) => l.resourceId === id)!;

describe("quantities", () => {
  it("rounds groups up", () => {
    expect(groupCount(25, 4)).toBe(7);
    expect(groupCount(24, 4)).toBe(6);
    expect(groupCount(1, 4)).toBe(1);
    expect(groupCount(32, 4)).toBe(8);
  });

  it("counts sheets, not cards, when several cards print on a page", () => {
    expect(copiesFor(8, 4)).toBe(2); // eight groups, four cards per sheet
    expect(copiesFor(7, 4)).toBe(2);
    expect(copiesFor(9, 4)).toBe(3);
    expect(copiesFor(9)).toBe(9);
  });

  it("rejects impossible numbers", () => {
    expect(quantityProblems({ studentCount: 0, groupSize: 4 })).toHaveLength(1);
    expect(quantityProblems({ studentCount: 25.5, groupSize: 4 })).toHaveLength(1);
    expect(quantityProblems({ studentCount: Number.NaN, groupSize: 4 })).toHaveLength(1);
    expect(quantityProblems({ studentCount: 25, groupSize: 0 })).toHaveLength(1);
    expect(quantityProblems({ studentCount: 25, groupSize: 4, copies: { x: -1 } })).toHaveLength(1);
    expect(quantityProblems({ studentCount: 25, groupSize: 4, copies: { x: 501 } })).toHaveLength(1);
    expect(quantityProblems({ studentCount: 25, groupSize: 4, copies: { x: 0 } })).toEqual([]);
  });
});

describe("computePlan", () => {
  it("always includes core worksheets and requires a choice", () => {
    const plan = computePlan(testLesson(), { choices: {}, extensions: {} }, q);
    expect(plan.problems).toContain("Choose one option for “Small Bite”.");
    expect(ids(plan)).toEqual(["core-sheet"]);
    expect(plan.lines[0].copies).toBe(25);
  });

  it("includes only the chosen option of an exclusive choice", () => {
    const plan = computePlan(testLesson(), { choices: { bite: "a" }, extensions: {} }, q);
    expect(plan.problems).toEqual([]);
    expect(ids(plan)).toEqual(["core-sheet", "song-sheet"]);
  });

  it("prints per-group cards as sheets", () => {
    const plan = computePlan(testLesson(), { choices: { bite: "b" }, extensions: {} }, { studentCount: 32, groupSize: 4 });
    expect(plan.groupCount).toBe(8);
    expect(line(plan, "team-cards")).toMatchObject({ needed: 8, defaultCopies: 2, copies: 2 });
  });

  it("ignores extensions of an option that is not chosen", () => {
    expect(ids(computePlan(testLesson(), { choices: { bite: "a" }, extensions: { "b-extra": true } }, q))).not.toContain("b-extra-sheet");
    expect(ids(computePlan(testLesson(), { choices: { bite: "b" }, extensions: { "b-extra": true } }, q))).toContain("b-extra-sheet");
  });

  it("adds independent extras only when checked, in lesson order", () => {
    expect(ids(computePlan(testLesson(), { choices: { bite: "c" }, extensions: {} }, q))).toEqual(["core-sheet"]);
    const both = computePlan(testLesson(), { choices: { bite: "a" }, extensions: { "group-sheet": true, poster: true } }, q);
    expect(ids(both)).toEqual(["core-sheet", "song-sheet", "poster", "group-sheet"]);
    expect(line(both, "poster").copies).toBe(1);
    expect(line(both, "group-sheet").copies).toBe(7);
  });

  it("lets the teacher set any worksheet's copies, and shows the default", () => {
    const plan = computePlan(testLesson(), { choices: { bite: "b" }, extensions: {} }, { ...q, copies: { "core-sheet": 30, "team-cards": 2 } });
    expect(line(plan, "core-sheet")).toMatchObject({ defaultCopies: 25, copies: 30, edited: true });
    expect(line(plan, "team-cards")).toMatchObject({ defaultCopies: 2, copies: 2, edited: false });
    const zero = computePlan(testLesson(), { choices: { bite: "c" }, extensions: {} }, { ...q, copies: { "core-sheet": 0 } });
    expect(zero.problems).toEqual(["Every worksheet is set to 0 copies."]);
  });

  it("lists unavailable worksheets separately and never prints them", () => {
    const plan = computePlan(testLesson(), { choices: { bite: "c" }, extensions: { locked: true } }, q);
    expect(ids(plan)).not.toContain("locked-sheet");
    expect(plan.unavailable).toEqual([
      { resourceId: "locked-sheet", title: "Locked Sheet", reason: "Coming soon: not published yet.", sources: ["Extras"] },
    ]);
  });

  it("prints a worksheet used twice once, at the larger default", () => {
    const plan = computePlan(testLesson(), { choices: { bite: "c" }, extensions: { reuse: true } }, q);
    expect(ids(plan)).toEqual(["core-sheet"]);
    expect(plan.lines[0]).toMatchObject({ copies: 25, rule: "per_student", sources: ["Core", "Extras"] });
  });
});

describe("printSequence", () => {
  const plan = computePlan(
    testLesson(),
    { choices: { bite: "b" }, extensions: { "b-extra": true, poster: true } },
    { studentCount: 3, groupSize: 2, copies: { "b-extra-sheet": 2 } },
  );

  it("groups copies by worksheet", () => {
    expect(printSequence(plan.lines, "worksheet")).toEqual([
      "core-sheet", "core-sheet", "core-sheet",
      "team-cards",
      "b-extra-sheet", "b-extra-sheet",
      "poster",
    ]);
  });

  it("makes one packet per student, then group and class copies", () => {
    expect(printSequence(plan.lines, "student")).toEqual([
      "core-sheet", "b-extra-sheet", // student 1
      "core-sheet", "b-extra-sheet", // student 2
      "core-sheet", // student 3 (only 2 extra copies were asked for)
      "team-cards",
      "poster",
    ]);
  });
});

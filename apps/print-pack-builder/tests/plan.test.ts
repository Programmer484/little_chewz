import { describe, expect, it } from "vitest";
import { computePlan, copiesFor, groupCount, printSequence, quantityProblems } from "../shared/plan.ts";
import { testLesson } from "./helpers.ts";

const q = { studentCount: 25 };
const none = { options: {}, extensions: {} };
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

  it("validates class size, group counts and overrides", () => {
    expect(quantityProblems({ studentCount: 0 })).toHaveLength(1);
    expect(quantityProblems({ studentCount: 25.5 })).toHaveLength(1);
    expect(quantityProblems({ ...q, groups: { a: 0 } })).toHaveLength(1);
    expect(quantityProblems({ ...q, groups: { a: 201 } })).toHaveLength(1);
    expect(quantityProblems({ ...q, groups: { a: 1 } })).toEqual([]);
    expect(quantityProblems({ ...q, copies: { a: -1 } })).toHaveLength(1);
    expect(quantityProblems({ ...q, copies: { a: 501 } })).toHaveLength(1);
    expect(quantityProblems({ ...q, copies: { a: 0 } })).toEqual([]);
  });
});

describe("selection", () => {
  it("starts with core ticked and warns, without blocking, about choices with nothing picked", () => {
    const plan = computePlan(testLesson(), none, q);
    expect(ids(plan)).toEqual(["core-sheet"]);
    expect(plan.lines[0].copies).toBe(25);
    expect(plan.problems).toEqual([]);
    expect(plan.warnings).toEqual(["Nothing picked for “Small Bite”."]);
    expect(computePlan(testLesson(), { ...none, options: { a: true } }, q).warnings).toEqual([]);
  });

  it("includes a picked option and its ticked extension, ignoring extensions of unpicked options", () => {
    const chosen = computePlan(testLesson(), { options: { b: true }, extensions: { "b-extra": true } }, q);
    expect(ids(chosen)).toEqual(["core-sheet", "team-cards", "b-extra-sheet"]);
    const ignored = computePlan(testLesson(), { options: { a: true }, extensions: { "b-extra": true } }, q);
    expect(ids(ignored)).toEqual(["core-sheet", "song-sheet"]);
  });

  it("allows both alternatives and unticking core, e.g. to print only an extension later", () => {
    const both = computePlan(testLesson(), { ...none, options: { a: true, b: true } }, q);
    expect(ids(both)).toEqual(["core-sheet", "song-sheet", "team-cards"]);
    const later = computePlan(testLesson(), { options: { b: true }, extensions: { "b-extra": true }, core: { "core:core-sheet": false } },
      { ...q, copies: { "team-cards:per_group:b": 0 } });
    expect(later.problems).toEqual([]);
    expect(later.lines.filter((l) => l.copies > 0).map((l) => l.resourceId)).toEqual(["b-extra-sheet"]);
  });

  it("rejects an empty pack or one where every copy is 0", () => {
    const empty = computePlan(testLesson(), { ...none, core: { "core:core-sheet": false } }, q);
    expect(empty.lines).toEqual([]);
    expect(empty.problems).toEqual(["Select at least one worksheet."]);
    const zero = computePlan(testLesson(), none, { ...q, copies: { "core-sheet:per_student": 0 } });
    expect(zero.problems).toEqual(["Every worksheet is set to 0 copies."]);
  });
});

describe("per-activity quantities", () => {
  it("defaults to students ÷ 4 groups, rounded up, with an editable count per activity", () => {
    const sel = { options: { b: true }, extensions: { "group-sheet": true } };
    const plan = computePlan(testLesson(), sel, { studentCount: 17 });
    expect(pick(plan, "group-sheet")).toMatchObject({ groups: 5, needed: 5, defaultCopies: 5 });
    const edited = computePlan(testLesson(), sel, { studentCount: 17, groups: { b: 4, "group-sheet": 6 } });
    expect(pick(edited, "team-cards")).toMatchObject({ groups: 4, needed: 4, defaultCopies: 1 });
    expect(pick(edited, "group-sheet")).toMatchObject({ groups: 6, needed: 6, defaultCopies: 6 });
  });

  it("treats a whole class as one group", () => {
    const plan = computePlan(testLesson(), { options: {}, extensions: { poster: true } }, { studentCount: 17, groups: { poster: 1 } });
    expect(pick(plan, "poster")).toMatchObject({ needed: 1, copies: 1 });
  });

  it("skips group copies of a sheet every student already gets, unless student copies are 0", () => {
    const sel = { options: {}, extensions: { reuse: true } };
    const plan = computePlan(testLesson(), sel, q);
    expect(ids(plan)).toEqual(["core-sheet"]);
    expect(pick(plan, "core-sheet")).toMatchObject({ rule: "per_student", copies: 25, sources: ["Core", "Reuse core"] });
    const zero = computePlan(testLesson(), sel, { ...q, copies: { "core-sheet:per_student": 0 } });
    expect(pick(zero, "core-sheet", "per_group")).toMatchObject({ copies: 7 });
  });

  it("keeps teacher copy overrides without changing defaults", () => {
    const plan = computePlan(testLesson(), { options: { b: true }, extensions: {} },
      { ...q, copies: { "core-sheet:per_student": 30, "team-cards:per_group:b": 3 } });
    expect(pick(plan, "core-sheet")).toMatchObject({ defaultCopies: 25, copies: 30, edited: true });
    expect(pick(plan, "team-cards")).toMatchObject({ defaultCopies: 2, copies: 3, edited: true });
  });

  it("shows unavailable materials but excludes them from downloaded pages", () => {
    const plan = computePlan(testLesson(), { options: {}, extensions: { locked: true } }, q);
    expect(ids(plan)).not.toContain("locked-sheet");
    expect(plan.unavailable).toMatchObject([{ resourceId: "locked-sheet" }]);
  });
});

describe("one fixed print sequence", () => {
  it("makes consecutive packets then shared copies grouped by resource", () => {
    const plan = computePlan(testLesson(),
      { options: { b: true }, extensions: { "b-extra": true, poster: true } },
      { studentCount: 3, copies: { "b-extra-sheet:per_student": 2 }, groups: { poster: 1 } });
    expect(printSequence(plan.lines)).toEqual({
      packets: [["core-sheet", "b-extra-sheet"], ["core-sheet", "b-extra-sheet"], ["core-sheet"]],
      shared: [
        { resourceId: "team-cards", frontOnly: true },
        { resourceId: "poster", frontOnly: false },
      ],
    });
  });
});

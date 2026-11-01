import { describe, expect, it } from "vitest";
import { computePlan, copiesFor, groupCount, quantityProblems } from "../shared/plan.ts";
import { testLesson } from "./helpers.ts";

const q = { studentCount: 25, groupSize: 4 };
const ids = (plan: ReturnType<typeof computePlan>) => plan.lines.map((l) => l.resourceId);

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

  it("rejects impossible class numbers", () => {
    expect(quantityProblems({ studentCount: 0, groupSize: 4 })).toHaveLength(1);
    expect(quantityProblems({ studentCount: 25.5, groupSize: 4 })).toHaveLength(1);
    expect(quantityProblems({ studentCount: Number.NaN, groupSize: 4 })).toHaveLength(1);
    expect(quantityProblems({ studentCount: 25, groupSize: 0 })).toHaveLength(1);
    expect(quantityProblems({ studentCount: 25, groupSize: 4, extra: { x: -1 } })).toHaveLength(1);
    expect(quantityProblems({ studentCount: 25, groupSize: 4 })).toEqual([]);
  });
});

describe("computePlan", () => {
  it("always includes core materials and requires a choice", () => {
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
    const cards = plan.lines.find((l) => l.resourceId === "team-cards")!;
    expect(plan.groupCount).toBe(8);
    expect(cards.needed).toBe(8);
    expect(cards.copies).toBe(2);
  });

  it("ignores extensions of an option that is not chosen", () => {
    const plan = computePlan(testLesson(), { choices: { bite: "a" }, extensions: { "b-extra": true } }, q);
    expect(ids(plan)).not.toContain("b-extra-sheet");
    const chosen = computePlan(testLesson(), { choices: { bite: "b" }, extensions: { "b-extra": true } }, q);
    expect(ids(chosen)).toContain("b-extra-sheet");
  });

  it("adds independent extras only when checked, in manifest order", () => {
    const none = computePlan(testLesson(), { choices: { bite: "c" }, extensions: {} }, q);
    expect(ids(none)).toEqual(["core-sheet"]);
    const both = computePlan(testLesson(), { choices: { bite: "a" }, extensions: { exit: true, poster: true } }, q);
    expect(ids(both)).toEqual(["core-sheet", "song-sheet", "poster", "exit-ticket"]);
    expect(both.lines.find((l) => l.resourceId === "poster")!.copies).toBe(1);
  });

  it("uses teacher-adjusted counts and spare copies", () => {
    const plan = computePlan(
      testLesson(),
      { choices: { bite: "b" }, extensions: { exit: true } },
      { ...q, adjusted: { "exit-ticket": 3 }, extra: { "core-sheet": 2, "team-cards": 1 } },
    );
    expect(plan.lines.find((l) => l.resourceId === "exit-ticket")!.copies).toBe(3);
    expect(plan.lines.find((l) => l.resourceId === "core-sheet")!.copies).toBe(27);
    expect(plan.lines.find((l) => l.resourceId === "team-cards")!.copies).toBe(3); // 7 groups -> 2 sheets + 1 spare
    const zero = computePlan(testLesson(), { choices: { bite: "c" }, extensions: { exit: true } }, { ...q, adjusted: { "exit-ticket": 0 } });
    expect(ids(zero)).not.toContain("exit-ticket");
  });

  it("totals pages only when every page count is verified", () => {
    const plan = computePlan(testLesson(), { choices: { bite: "b" }, extensions: {} }, q);
    expect(plan.totalPages).toBe(25 * 2 + 2 * 1);
    const unknown = computePlan(testLesson(), { choices: { bite: "b" }, extensions: { exit: true } }, q);
    expect(unknown.totalPages).toBeNull();
  });

  it("lists unavailable materials separately and never prints them", () => {
    const plan = computePlan(testLesson(), { choices: { bite: "c" }, extensions: { locked: true } }, q);
    expect(ids(plan)).not.toContain("locked-sheet");
    expect(plan.unavailable).toEqual([
      { resourceId: "locked-sheet", title: "Locked Sheet", reason: "Awaiting review for the pilot.", sources: ["Locked"] },
    ]);
  });

  it("prints a resource used twice once, at the larger quantity", () => {
    const plan = computePlan(testLesson(), { choices: { bite: "c" }, extensions: { reuse: true } }, q);
    expect(ids(plan)).toEqual(["core-sheet"]);
    expect(plan.lines[0].copies).toBe(25);
    expect(plan.lines[0].sources).toEqual(["Core", "Reuse core"]);
  });

  it("blocks packs over the page limit", () => {
    const lesson = testLesson();
    const core = lesson.sections[0];
    if (core.kind !== "core") throw new Error("fixture changed");
    core.materials[0].pages = 8;
    const plan = computePlan(lesson, { choices: { bite: "c" }, extensions: {} }, { studentCount: 200, groupSize: 4 });
    expect(plan.totalPages).toBe(1600);
    expect(plan.problems.join(" ")).toMatch(/over the 1500-page limit/);
  });
});

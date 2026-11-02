import { LIMITS } from "./limits.ts";
import type { Plan, PlanLine, PrintSequence, Quantities, ResolvedLesson, ResolvedMaterial, Selection } from "./types.ts";

export const groupCount = (students: number, size: number) => Math.ceil(students / size);
const whole = (n: unknown): n is number => typeof n === "number" && Number.isInteger(n);

export function quantityProblems(q: Quantities): string[] {
  const errors: string[] = [];
  if (!whole(q.studentCount) || q.studentCount < LIMITS.minStudents || q.studentCount > LIMITS.maxStudents)
    errors.push(`Enter a student count from ${LIMITS.minStudents} to ${LIMITS.maxStudents}.`);
  if ([q.groupSize, ...Object.values(q.groupSizes ?? {})].some((n) =>
    !whole(n) || n < LIMITS.minGroupSize || n > LIMITS.maxGroupSize))
    errors.push(`Enter a group size from ${LIMITS.minGroupSize} to ${LIMITS.maxGroupSize}.`);
  if (Object.values(q.copies ?? {}).some((n) => n !== undefined && (!whole(n) || n < 0 || n > LIMITS.maxCopies)))
    errors.push(`Copies must be a whole number from 0 to ${LIMITS.maxCopies}.`);
  return errors;
}

/** A multi-card sheet supplies several cutouts from one printed copy. */
export const copiesFor = (needed: number, cardsPerSheet?: number) =>
  cardsPerSheet ? Math.ceil(needed / cardsPerSheet) : needed;

export interface SelectedPick {
  material: ResolvedMaterial;
  source: string;
  activityId: string;
}

/** All selected activities, in lesson order. Choice groups may be left unanswered. */
export function selectedMaterials(lesson: ResolvedLesson, sel: Selection): { problems: string[]; picks: SelectedPick[] } {
  const picks: SelectedPick[] = [];
  for (const s of lesson.sections) {
    if (s.kind === "core") for (const m of s.materials)
      if (!sel.customize || sel.materials?.[`${s.id}:${m.resourceId}`] !== false)
        picks.push({ material: m, source: s.title, activityId: s.id });
    if (s.kind === "choice") {
      const options = s.options.filter((o) => sel.customize
        ? (sel.customChoices?.[o.id] ?? (sel.choices[s.id] === o.id))
        : sel.choices[s.id] === o.id);
      for (const chosen of options) {
        const label = `${chosen.label} · ${chosen.title}`;
        for (const m of chosen.materials)
          if (!sel.customize || sel.materials?.[`${chosen.id}:${m.resourceId}`] !== false)
            picks.push({ material: m, source: label, activityId: chosen.id });
        for (const e of chosen.extensions)
          if (sel.extensions[e.id]) for (const m of e.materials)
            picks.push({ material: m, source: `${label} · ${e.title}`, activityId: e.id });
      }
    }
    if (s.kind === "optional")
      for (const item of s.items)
        if (sel.extensions[item.id]) for (const m of item.materials)
          picks.push({ material: m, source: item.title, activityId: item.id });
  }
  const problems = sel.customize ? [] : lesson.sections
    .filter((s) => s.kind === "choice" && !s.options.some((o) => o.id === sel.choices[s.id]))
    .map((s) => `Choose one option for “${s.title}”.`);
  return { problems, picks };
}

/** Keep per-group uses separate, even when they point to the same resource ID. */
export function computePlan(lesson: ResolvedLesson, sel: Selection, q: Quantities): Plan {
  const problems = quantityProblems(q);
  const { picks, problems: choiceProblems } = selectedMaterials(lesson, sel);
  problems.push(...choiceProblems);
  if (lesson.status !== "ready") problems.push("This lesson has no downloadable student materials yet.");

  const lines = new Map<string, PlanLine>();
  const unavailable = new Map<string, Plan["unavailable"][number]>();
  for (const { material: m, source, activityId } of picks) {
    if (!m.resource.available) {
      const item = unavailable.get(m.resourceId);
      if (item) { if (!item.sources.includes(source)) item.sources.push(source); }
      else unavailable.set(m.resourceId, {
        resourceId: m.resourceId, title: m.resource.title,
        reason: m.resource.reason ?? "Not available yet.", sources: [source],
      });
      continue;
    }
    const size = m.rule === "per_group" ? (q.groupSizes?.[activityId] ?? q.groupSize) : undefined;
    const needed = problems.length ? 0 : m.rule === "per_student" ? q.studentCount : groupCount(q.studentCount, size!);
    const id = `${m.resourceId}:${m.rule}${m.rule === "per_group" ? `:${activityId}` : ""}`;
    const previous = lines.get(id);
    if (previous) {
      if (!previous.sources.includes(source)) previous.sources.push(source);
      continue;
    }
    const defaultCopies = copiesFor(needed, m.cardsPerSheet);
    const override = q.copies?.[id];
    lines.set(id, {
      id, activityId, resourceId: m.resourceId, title: m.resource.title, rule: m.rule,
      ...(size !== undefined ? { groupSize: size } : {}),
      needed, cardsPerSheet: m.cardsPerSheet, defaultCopies,
      copies: override ?? defaultCopies, edited: override !== undefined && override !== defaultCopies,
      sources: [source], note: m.note,
    });
  }
  const all = [...lines.values()];
  if (!problems.length && all.every((l) => l.copies === 0))
    problems.push(unavailable.size
      ? "None of the selected worksheets can be downloaded yet."
      : all.length ? "Every worksheet is set to 0 copies." : "Select at least one worksheet.");
  return { lines: all, unavailable: [...unavailable.values()], problems };
}

export function describeLine(line: PlanLine, q: Pick<Quantities, "studentCount">): string {
  const units = line.cardsPerSheet
    ? `${line.needed} cutouts, ${line.cardsPerSheet} per sheet`
    : line.rule === "per_student"
      ? `One per student (${q.studentCount})`
      : `One per group (${groupCount(q.studentCount, line.groupSize!)} groups)`;
  return units;
}

/** Student packets first, in lesson order; shared resources grouped by copy. */
export function printSequence(lines: PlanLine[]): PrintSequence {
  const printed = lines.filter((line) => line.copies > 0);
  const student = printed.filter((line) => line.rule === "per_student" && !line.cardsPerSheet);
  const shared = printed.filter((line) => !student.includes(line));
  // Keep one resource's shared copies together, even across distinct activities.
  const sharedGroups = new Map<string, PlanLine[]>();
  for (const line of shared) sharedGroups.set(line.resourceId, [...(sharedGroups.get(line.resourceId) ?? []), line]);
  const count = Math.max(0, ...student.map((line) => line.copies));
  const packets: string[][] = [];
  for (let i = 0; i < count; i++)
    packets.push(student.filter((line) => i < line.copies).map((line) => line.resourceId));
  return { packets, shared: [...sharedGroups.values()].flatMap((group) => group.flatMap((line) =>
    Array.from({ length: line.copies }, () => ({ resourceId: line.resourceId, frontOnly: (line.cardsPerSheet ?? 0) > 1 })))) };
}

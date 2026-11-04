import { LIMITS } from "./limits.ts";
import type { Plan, PlanLine, PrintSequence, Quantities, ResolvedExtension, ResolvedLesson, ResolvedMaterial, Selection } from "./types.ts";

export const groupCount = (students: number, size: number) => Math.ceil(students / size);
const whole = (n: unknown): n is number => typeof n === "number" && Number.isInteger(n);

export function quantityProblems(q: Quantities): string[] {
  const errors: string[] = [];
  if (!whole(q.studentCount) || q.studentCount < LIMITS.minStudents || q.studentCount > LIMITS.maxStudents)
    errors.push(`Enter a student count from ${LIMITS.minStudents} to ${LIMITS.maxStudents}.`);
  if (Object.values(q.groupSizes ?? {}).some((n) => n !== undefined && (!whole(n) || n < 1 || n > LIMITS.maxStudents)))
    errors.push(`Students per group must be a whole number from 1 to ${LIMITS.maxStudents}.`);
  if (Object.values(q.groups ?? {}).some((n) => n !== undefined && (!whole(n) || n < 1 || n > LIMITS.maxGroups)))
    errors.push(`Enter a number of groups from 1 to ${LIMITS.maxGroups}.`);
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
  /** The chosen option's default students per group, if it sets one. */
  groupSize?: number;
}

/** Ticked worksheets, in lesson order. */
export function selectedMaterials(lesson: ResolvedLesson, sel: Selection): SelectedPick[] {
  const picks: SelectedPick[] = [];
  const extras = (items: ResolvedExtension[], prefix = "") => {
    for (const e of items) if (sel.extensions[e.id]) for (const m of e.materials)
      picks.push({ material: m, source: prefix + e.title, activityId: e.id });
  };
  for (const s of lesson.sections) {
    if (s.kind === "core") for (const m of s.materials)
      if (sel.core?.[`${s.id}:${m.resourceId}`] !== false) picks.push({ material: m, source: s.title, activityId: s.id });
    if (s.kind === "choice") for (const option of s.options) {
      if (!sel.options[option.id]) continue;
      const label = `${option.label} · ${option.title}`;
      for (const m of option.materials)
        picks.push({ material: m, source: label, activityId: option.id, ...(option.groupSize ? { groupSize: option.groupSize } : {}) });
      extras(option.extensions, `${label} · `);
    }
    if (s.kind === "optional") extras(s.items);
  }
  return picks;
}

/** Per-group uses of one resource stay separate by activity, unless every student already gets that resource. */
export function computePlan(lesson: ResolvedLesson, sel: Selection, q: Quantities): Plan {
  const numberProblems = quantityProblems(q);
  const problems = [...numberProblems];
  if (lesson.status !== "ready") problems.push("This lesson has no downloadable student materials yet.");
  const lines = new Map<string, PlanLine>();
  const unavailable = new Map<string, Plan["unavailable"][number]>();
  for (const { material: m, source, activityId, groupSize } of selectedMaterials(lesson, sel)) {
    if (!m.resource.available) {
      const item = unavailable.get(m.resourceId);
      if (item) { if (!item.sources.includes(source)) item.sources.push(source); }
      else unavailable.set(m.resourceId, {
        resourceId: m.resourceId, title: m.resource.title,
        reason: m.resource.reason ?? "Not available yet.", sources: [source],
      });
      continue;
    }
    const defaultGroupSize = groupSize ?? lesson.defaults.groupSize;
    const groups = m.rule === "per_group"
      ? (q.groups?.[activityId] ?? groupCount(q.studentCount, q.groupSizes?.[activityId] ?? defaultGroupSize))
      : undefined;
    const needed = numberProblems.length ? 0 : m.rule === "per_student" ? q.studentCount : groups!;
    const id = `${m.resourceId}:${m.rule}${m.rule === "per_group" ? `:${activityId}` : ""}`;
    const previous = lines.get(id);
    if (previous) {
      if (!previous.sources.includes(source)) previous.sources.push(source);
      continue;
    }
    const defaultCopies = copiesFor(needed, m.cardsPerSheet);
    const override = q.copies?.[id];
    lines.set(id, {
      id, activityId, ...(m.rule === "per_group" ? { defaultGroupSize } : {}), resourceId: m.resourceId, title: m.resource.title, rule: m.rule,
      ...(groups !== undefined ? { groups } : {}),
      needed, cardsPerSheet: m.cardsPerSheet, defaultCopies,
      copies: override ?? defaultCopies, edited: override !== undefined && override !== defaultCopies,
      sources: [source], note: m.note,
    });
  }
  // A sheet already in every student's packet needs no extra group copies.
  // Setting the student copies to 0 brings the group copies back.
  for (const group of [...lines.values()].filter((l) => l.rule === "per_group")) {
    const student = lines.get(`${group.resourceId}:per_student`);
    if (!student || student.copies === 0) continue;
    for (const source of group.sources) if (!student.sources.includes(source)) student.sources.push(source);
    lines.delete(group.id);
  }
  const all = [...lines.values()];
  if (!problems.length && all.every((l) => l.copies === 0))
    problems.push(unavailable.size
      ? "None of the selected worksheets can be downloaded yet."
      : all.length ? "Every worksheet is set to 0 copies." : "Select at least one worksheet.");
  const warnings = lesson.sections
    .filter((s) => s.kind === "choice" && !s.options.some((o) => sel.options[o.id]))
    .map((s) => `Nothing picked for “${s.title}”.`);
  return { lines: all, unavailable: [...unavailable.values()], problems, warnings };
}

/** Short copy rule shown beside each copies box. */
export function describeLine(line: PlanLine): string {
  const each = line.rule === "per_student" ? "1 per student" : "1 per group";
  return line.cardsPerSheet ? `${each}, ${line.cardsPerSheet} per sheet` : each;
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

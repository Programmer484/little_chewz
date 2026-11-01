import { LIMITS } from "./limits.ts";
import type { Plan, PlanLine, Quantities, ResolvedLesson, ResolvedMaterial, Selection } from "./types.ts";

export function groupCount(studentCount: number, groupSize: number): number {
  return Math.ceil(studentCount / groupSize);
}

const whole = (n: unknown): n is number => typeof n === "number" && Number.isInteger(n);

/** Problems with the class numbers, in plain language. */
export function quantityProblems(q: Quantities): string[] {
  const p: string[] = [];
  if (!whole(q.studentCount) || q.studentCount < LIMITS.minStudents || q.studentCount > LIMITS.maxStudents)
    p.push(`Enter a student count from ${LIMITS.minStudents} to ${LIMITS.maxStudents}.`);
  if (!whole(q.groupSize) || q.groupSize < LIMITS.minGroupSize || q.groupSize > LIMITS.maxGroupSize)
    p.push(`Enter a group size from ${LIMITS.minGroupSize} to ${LIMITS.maxGroupSize}.`);
  for (const [id, n] of Object.entries(q.extra ?? {}))
    if (n !== undefined && (!whole(n) || n < 0 || n > LIMITS.maxExtraCopies))
      p.push(`Extra copies for ${id} must be 0–${LIMITS.maxExtraCopies}.`);
  for (const [id, n] of Object.entries(q.adjusted ?? {}))
    if (n !== undefined && (!whole(n) || n < 0 || n > LIMITS.maxAdjustedCopies))
      p.push(`Copies for ${id} must be 0–${LIMITS.maxAdjustedCopies}.`);
  return p;
}

/** Copies (or cards) one placement of a material needs. */
export function neededFor(m: ResolvedMaterial, q: Quantities, groups: number): number {
  switch (m.quantity.rule) {
    case "per_student":
      return q.studentCount;
    case "per_group":
      return groups;
    case "per_class":
    case "per_activity":
      return m.quantity.count ?? 1;
    case "teacher_adjustable":
      return q.adjusted?.[m.resourceId] ?? m.quantity.count ?? 1;
  }
}

/** File copies to print for a need, honouring cards printed several to a sheet. */
export function copiesFor(needed: number, cardsPerSheet?: number): number {
  return cardsPerSheet ? Math.ceil(needed / cardsPerSheet) : needed;
}

/** Selected materials, in manifest order, each tagged with where it came from. */
export function selectedMaterials(
  lesson: ResolvedLesson,
  sel: Selection,
): { problems: string[]; picks: { material: ResolvedMaterial; source: string }[] } {
  const problems: string[] = [];
  const picks: { material: ResolvedMaterial; source: string }[] = [];
  for (const s of lesson.sections) {
    if (s.kind === "core") for (const m of s.materials) picks.push({ material: m, source: s.title });
    if (s.kind === "choice") {
      const chosen = s.options.find((o) => o.id === sel.choices[s.id]);
      if (!chosen) {
        problems.push(`Choose one option for “${s.title}”.`);
        continue;
      }
      const label = `${chosen.label} · ${chosen.title}`;
      for (const m of chosen.materials) picks.push({ material: m, source: label });
      for (const e of chosen.extensions)
        if (sel.extensions[e.id]) for (const m of e.materials) picks.push({ material: m, source: e.title });
    }
    if (s.kind === "optional")
      for (const item of s.items)
        if (sel.extensions[item.id]) for (const m of item.materials) picks.push({ material: m, source: item.title });
  }
  return { problems, picks };
}

/**
 * The print plan: one line per distinct resource, in first-use order.
 * A resource used by several selected activities is printed once, at the
 * largest quantity any of them needs.
 */
export function computePlan(lesson: ResolvedLesson, sel: Selection, q: Quantities): Plan {
  const problems = quantityProblems(q);
  const groups = problems.length ? 0 : groupCount(q.studentCount, q.groupSize);
  const { problems: choiceProblems, picks } = selectedMaterials(lesson, sel);
  problems.push(...choiceProblems);
  if (lesson.status !== "ready") problems.push("This lesson has no downloadable student materials yet.");

  const lines = new Map<string, PlanLine>();
  const unavailable = new Map<string, Plan["unavailable"][number]>();
  for (const { material: m, source } of picks) {
    if (!m.resource.available) {
      const u = unavailable.get(m.resourceId);
      if (u) u.sources.push(source);
      else
        unavailable.set(m.resourceId, {
          resourceId: m.resourceId,
          title: m.resource.title,
          reason: m.resource.reason ?? "Not available yet.",
          sources: [source],
        });
      continue;
    }
    const needed = groups ? neededFor(m, q, groups) : 0;
    const line = lines.get(m.resourceId);
    if (line) {
      line.needed = Math.max(line.needed, needed);
      if (!line.sources.includes(source)) line.sources.push(source);
    } else
      lines.set(m.resourceId, {
        resourceId: m.resourceId,
        title: m.resource.title,
        rule: m.quantity.rule,
        needed,
        cardsPerSheet: m.cardsPerSheet,
        extra: 0,
        copies: 0,
        pagesPerCopy: m.pages,
        sources: [source],
        note: m.note,
      });
  }
  for (const line of lines.values()) {
    line.extra = q.extra?.[line.resourceId] ?? 0;
    line.copies = copiesFor(line.needed, line.cardsPerSheet) + line.extra;
  }
  const printed = [...lines.values()].filter((l) => l.copies > 0);
  const totalPages = printed.every((l) => l.pagesPerCopy)
    ? printed.reduce((sum, l) => sum + l.copies * (l.pagesPerCopy ?? 0), 0)
    : null;
  if (totalPages !== null && totalPages > LIMITS.maxTotalPages)
    problems.push(
      `This pack would be ${totalPages} pages, over the ${LIMITS.maxTotalPages}-page limit. Lower the quantities or download in two parts.`,
    );
  if (!problems.length && printed.length === 0)
    problems.push(
      unavailable.size
        ? "None of the materials for these choices can be downloaded yet."
        : "These choices need no student printing.",
    );
  return { groupCount: groups, lines: printed, unavailable: [...unavailable.values()], problems, totalPages };
}

export function describeLine(line: PlanLine, q: Pick<Quantities, "studentCount">, groups: number): string {
  if (line.cardsPerSheet)
    return `${line.needed} card${line.needed === 1 ? "" : "s"}, ${line.cardsPerSheet} per sheet`;
  switch (line.rule) {
    case "per_student":
      return `One per student (${q.studentCount})`;
    case "per_group":
      return `One per group (${groups} groups)`;
    case "per_class":
      return line.needed === 1 ? "One for the class" : `${line.needed} for the class`;
    case "per_activity":
      return line.needed === 1 ? "One for the activity" : `${line.needed} for the activity`;
    case "teacher_adjustable":
      return "Your quantity";
  }
}

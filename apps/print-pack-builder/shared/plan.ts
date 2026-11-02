import { LIMITS } from "./limits.ts";
import type { Plan, PlanLine, PrintOptions, Quantities, ResolvedLesson, ResolvedMaterial, Selection } from "./types.ts";

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
  for (const n of Object.values(q.copies ?? {}))
    if (n !== undefined && (!whole(n) || n < 0 || n > LIMITS.maxCopies)) {
      p.push(`Copies must be a whole number from 0 to ${LIMITS.maxCopies}.`);
      break;
    }
  return p;
}

/** Copies (or cards) the default rule asks for. */
export function neededFor(m: Pick<ResolvedMaterial, "rule">, q: Quantities, groups: number): number {
  switch (m.rule) {
    case "per_student":
      return q.studentCount;
    case "per_group":
      return groups;
    case "per_class":
      return 1;
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
        if (sel.extensions[e.id]) for (const m of e.materials) picks.push({ material: m, source: `${label} · optional` });
    }
    if (s.kind === "optional")
      for (const item of s.items)
        if (sel.extensions[item.id]) for (const m of item.materials) picks.push({ material: m, source: s.title });
  }
  return { problems, picks };
}

/**
 * The print plan: one line per distinct worksheet, in first-use order.
 * Defaults come from each worksheet's rule; a number the teacher typed
 * replaces the default. A worksheet used by several selected activities is
 * printed once, at the largest default.
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
      if (needed > line.needed) Object.assign(line, { needed, rule: m.rule, note: m.note });
      if (!line.sources.includes(source)) line.sources.push(source);
    } else
      lines.set(m.resourceId, {
        resourceId: m.resourceId,
        title: m.resource.title,
        rule: m.rule,
        needed,
        cardsPerSheet: m.cardsPerSheet,
        defaultCopies: 0,
        copies: 0,
        edited: false,
        sources: [source],
        note: m.note,
      });
  }
  for (const line of lines.values()) {
    line.defaultCopies = copiesFor(line.needed, line.cardsPerSheet);
    const typed = q.copies?.[line.resourceId];
    line.edited = typed !== undefined && typed !== line.defaultCopies;
    line.copies = typed ?? line.defaultCopies;
  }
  const all = [...lines.values()];
  if (!problems.length && all.every((l) => l.copies === 0))
    problems.push(
      unavailable.size
        ? "None of the worksheets for these choices can be downloaded yet."
        : all.length
          ? "Every worksheet is set to 0 copies."
          : "These choices need no student printing.",
    );
  return { groupCount: groups, lines: all, unavailable: [...unavailable.values()], problems };
}

export function describeLine(line: PlanLine, q: Pick<Quantities, "studentCount">, groups: number): string {
  if (line.cardsPerSheet)
    return `${line.needed} card${line.needed === 1 ? "" : "s"} (one per ${line.rule === "per_group" ? "group" : line.rule === "per_class" ? "class" : "student"}), ${line.cardsPerSheet} per sheet`;
  switch (line.rule) {
    case "per_student":
      return `One per student (${q.studentCount})`;
    case "per_group":
      return `One per group (${groups} groups)`;
    case "per_class":
      return "One for the class";
  }
}

/**
 * The order copies appear in the PDF, as a list of resource IDs (one entry per
 * copy of the whole file).
 *
 * - "worksheet": every copy of the first worksheet, then the next.
 * - "student": one packet per student, holding one copy of each per-student
 *   worksheet; worksheets for groups or the class follow, by worksheet.
 */
export function printSequence(lines: PlanLine[], order: PrintOptions["order"]): string[] {
  const printed = lines.filter((l) => l.copies > 0);
  const byWorksheet = (ls: PlanLine[]) => ls.flatMap((l) => Array<string>(l.copies).fill(l.resourceId));
  if (order === "worksheet") return byWorksheet(printed);
  const packet = printed.filter((l) => l.rule === "per_student" && !l.cardsPerSheet);
  const rest = printed.filter((l) => !packet.includes(l));
  const packets = Math.max(0, ...packet.map((l) => l.copies));
  const out: string[] = [];
  for (let i = 0; i < packets; i++) for (const l of packet) if (i < l.copies) out.push(l.resourceId);
  return [...out, ...byWorksheet(rest)];
}

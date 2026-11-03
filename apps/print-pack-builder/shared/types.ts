/**
 * Shared types for the browser app and the Worker.
 *
 * Real lessons are not configured here: shared/derive.ts reads each lesson's
 * Teacher Guide source (lesson.json) and catalog/resources.json and produces
 * a LessonManifest. Only the synthetic demo lesson is written by hand.
 */

/** Default copies for a material. Teachers can change any line's copies. */
export type QuantityRule = "per_student" | "per_group";

export interface MaterialSpec {
  resourceId: string;
  rule: QuantityRule;
  /**
   * Identical cards printed on every page, from the catalogue's
   * print.cards_per_sheet. The rule then counts cards, and the plan prints
   * ceil(cardsNeeded / cardsPerSheet) copies of the file.
   */
  cardsPerSheet?: number;
  /** Teacher Guide description, e.g. "One per group of 3–4". */
  note?: string;
}

/** An independent, checkbox-style extra. */
export interface ExtensionSpec {
  id: string;
  title: string;
  summary?: string;
  materials: MaterialSpec[];
}

/** One alternative in a mutually exclusive choice (A, B, C...). */
export interface OptionSpec {
  id: string;
  label: string;
  title: string;
  summary?: string;
  /** Default students per group for this option's per-group materials (lesson.json `group_size`). */
  groupSize?: number;
  materials: MaterialSpec[];
  /** Checkbox extras that only apply when this option is chosen. */
  extensions?: ExtensionSpec[];
}

export type SectionSpec =
  | { kind: "core"; id: string; title: string; summary?: string; materials: MaterialSpec[] }
  | { kind: "choice"; id: string; title: string; summary?: string; options: OptionSpec[] }
  | { kind: "optional"; id: string; title: string; summary?: string; items: ExtensionSpec[] };

export type LessonStatus = "ready" | "no_student_printing" | "in_progress";

export interface LessonManifest {
  lessonId: string;
  questId: string;
  order: number;
  title: string;
  status: LessonStatus;
  statusNote?: string;
  defaults?: { studentCount?: number; groupSize?: number };
  sections: SectionSpec[];
}

export interface QuestInfo {
  id: string;
  title: string;
  order: number;
}

export type AllowedMime = "application/pdf" | "image/png" | "image/jpeg";

/* ---------------- Client-facing (sanitized) shapes ---------------- */

/** A resource as the browser sees it: no Drive IDs or URLs. */
export interface ClientResource {
  id: string;
  title: string;
  available: boolean;
  /** Plain-language reason when unavailable. */
  reason?: string;
}

export interface ResolvedMaterial extends MaterialSpec {
  resource: ClientResource;
}

export interface ResolvedExtension extends Omit<ExtensionSpec, "materials"> {
  materials: ResolvedMaterial[];
}

export interface ResolvedOption extends Omit<OptionSpec, "materials" | "extensions"> {
  materials: ResolvedMaterial[];
  extensions: ResolvedExtension[];
}

export type ResolvedSection =
  | { kind: "core"; id: string; title: string; summary?: string; materials: ResolvedMaterial[] }
  | { kind: "choice"; id: string; title: string; summary?: string; options: ResolvedOption[] }
  | { kind: "optional"; id: string; title: string; summary?: string; items: ResolvedExtension[] };

export interface ResolvedLesson {
  lessonId: string;
  questId: string;
  questTitle: string;
  order: number;
  title: string;
  status: LessonStatus;
  statusNote?: string;
  defaults: { studentCount: number; groupSize: number };
  sections: ResolvedSection[];
  /** True when the lesson is ready and at least one material can be downloaded. */
  printable: boolean;
  demo?: boolean;
}

export interface LessonsResponse {
  mode: ResourceMode;
  lessons: ResolvedLesson[];
}

export type ResourceMode = "disabled" | "demo" | "drive";

/* ---------------- Selections, plan and print options ---------------- */

/** Everything is a checkbox: core worksheets start ticked, options and extras start unticked. */
export interface Selection {
  /** option id -> picked. A choice may have one, several or no options picked. */
  options: Record<string, boolean | undefined>;
  /** extension id -> checked */
  extensions: Record<string, boolean | undefined>;
  /** `${sectionId}:${resourceId}` -> false when the teacher unticks a core worksheet. */
  core?: Record<string, boolean | undefined>;
}

export interface Quantities {
  studentCount: number;
  /** activity id -> students per group; overrides the lesson default. */
  groupSizes?: Record<string, number | undefined>;
  /** Legacy direct group-count override, retained for existing callers. */
  groups?: Record<string, number | undefined>;
  /** plan line id -> copies the teacher typed, replacing the default. */
  copies?: Record<string, number | undefined>;
}

export interface PlanLine {
  id: string;
  activityId: string;
  /** Students per group used when the teacher has not changed it. */
  defaultGroupSize?: number;
  /** Number of groups, for per_group lines. */
  groups?: number;
  resourceId: string;
  title: string;
  rule: QuantityRule;
  /** Copies (or cards, when cardsPerSheet is set) the default rule asks for. */
  needed: number;
  cardsPerSheet?: number;
  /** Copies of the file the default rule prints. */
  defaultCopies: number;
  /** Copies of the file to print: the teacher's number, or the default. */
  copies: number;
  /** True when the teacher changed the copies. */
  edited: boolean;
  /** Where the material comes from, e.g. "Step 1 · Clue Hunt", "B · Character Profile". */
  sources: string[];
  note?: string;
}

export interface Plan {
  lines: PlanLine[];
  /** Selected materials that cannot be downloaded yet. */
  unavailable: { resourceId: string; title: string; reason: string; sources: string[] }[];
  /** Blocking problems, e.g. invalid quantities. */
  problems: string[];
  /** Non-blocking reminders, e.g. a choice with nothing picked. */
  warnings: string[];
}

/** One PDF, always arranged as consecutive student packets then shared materials. */
export interface PrintOptions {
  duplex: boolean;
}

/** Boundaries are explicit: duplex padding belongs to packets, not worksheets. */
export interface PrintSequence {
  packets: string[][];
  shared: { resourceId: string; frontOnly: boolean }[];
}

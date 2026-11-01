/**
 * Print manifest and plan types shared by the browser app and the Worker.
 * Manifests live in config/lessons/*.json and reference stable IDs from
 * catalog/resources.json. They never contain Drive IDs or URLs.
 */

/** How many copies of a material a class needs. */
export type QuantityRule =
  | "per_student" // one per student
  | "per_group" // one per group: ceil(students / groupSize)
  | "per_class" // a fixed count for the whole class (default 1)
  | "per_activity" // a fixed count each time its activity is selected (default 1)
  | "teacher_adjustable"; // a default count the teacher can change

export interface QuantitySpec {
  rule: QuantityRule;
  /** Fixed or default count for per_class, per_activity and teacher_adjustable. */
  count?: number;
}

export interface MaterialSpec {
  resourceId: string;
  quantity: QuantitySpec;
  /**
   * Verified number of identical cards printed on every page of the file.
   * When set, the rule counts cards, and the plan prints
   * ceil(cardsNeeded / cardsPerSheet) copies of the file.
   */
  cardsPerSheet?: number;
  /** Verified page count of one copy, used for estimates before download. */
  pages?: number;
  /** Short teacher-facing note, e.g. "One per group of 3–4". */
  note?: string;
}

/** An independent, checkbox-style extra. */
export interface ExtensionSpec {
  id: string;
  title: string;
  summary?: string;
  materials: MaterialSpec[];
}

/** One alternative in a mutually exclusive choice. */
export interface OptionSpec {
  id: string;
  label: string; // "A", "B", ...
  title: string;
  summary?: string;
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
  /** Lesson folder in the quest's quest.json learning_sequence (alignment check). */
  lessonFolder?: string;
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

/** Pilot allowlist: the only resources the Worker will ever serve. */
export interface PilotAllowEntry {
  /** Which registry URL is the trusted source. Only "published" is used for the pilot. */
  source: "published" | "holding";
  mimeType: AllowedMime;
  /** Why this resource is allowed; required for "holding" sources. */
  approval: string;
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

/* ---------------- Selections and plan ---------------- */

export interface Selection {
  /** sectionId -> chosen optionId */
  choices: Record<string, string | undefined>;
  /** extension id -> checked */
  extensions: Record<string, boolean | undefined>;
}

export interface Quantities {
  studentCount: number;
  groupSize: number;
  /** resourceId -> teacher-set count for teacher_adjustable materials */
  adjusted?: Record<string, number | undefined>;
  /** resourceId -> extra spare copies */
  extra?: Record<string, number | undefined>;
}

export interface PlanLine {
  resourceId: string;
  title: string;
  rule: QuantityRule;
  /** Copies (or cards, when cardsPerSheet is set) the class needs, before extras. */
  needed: number;
  cardsPerSheet?: number;
  /** Spare copies of the file added by the teacher. */
  extra: number;
  /** Copies of the file to print (what the PDF contains). */
  copies: number;
  /** Pages in one copy, when verified. */
  pagesPerCopy?: number;
  /** Where the material comes from, e.g. "Core", "Small Bite B". */
  sources: string[];
  note?: string;
}

export interface Plan {
  groupCount: number;
  lines: PlanLine[];
  /** Selected materials that cannot be downloaded yet. */
  unavailable: { resourceId: string; title: string; reason: string; sources: string[] }[];
  /** Blocking problems, e.g. an unanswered choice. */
  problems: string[];
  /** Total pages when every line has a verified page count, else null. */
  totalPages: number | null;
}

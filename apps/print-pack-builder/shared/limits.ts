/** Practical limits shared by the Worker and the browser. */
export const LIMITS = {
  minStudents: 1,
  maxStudents: 200,
  minGroupSize: 1,
  maxGroupSize: 30,
  maxExtraCopies: 100,
  maxAdjustedCopies: 200,
  /** Largest single worksheet file the Worker or browser will accept. */
  maxResourceBytes: 25 * 1024 * 1024,
  /** Largest combined packet, in pages. */
  maxTotalPages: 1500,
  /** Largest sum of distinct source files in one packet. */
  maxTotalSourceBytes: 120 * 1024 * 1024,
} as const;

export const DEFAULT_STUDENT_COUNT = 25;
export const DEFAULT_GROUP_SIZE = 4;

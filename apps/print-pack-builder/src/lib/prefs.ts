/**
 * Remember a teacher's class size and print settings on this device only
 * (browser localStorage). Nothing is sent anywhere. Every access is guarded:
 * private windows and blocked storage simply fall back to the defaults.
 */
import { LIMITS } from "../../shared/limits.ts";
import type { PrintOptions } from "../../shared/types.ts";

export interface Prefs extends PrintOptions {
  studentCount?: number;
}

const KEY = "little-chewz-print-pack:prefs";
export const DEFAULT_PRINT: PrintOptions = { duplex: false };

const inRange = (n: unknown, min: number, max: number): n is number => Number.isInteger(n) && (n as number) >= min && (n as number) <= max;

/** The browser's storage; reading it can itself throw (blocked or private mode). */
const browserStorage = (): Storage | null => globalThis.localStorage ?? null;

export function loadPrefs(storage?: Pick<Storage, "getItem"> | null): Prefs {
  try {
    const store = storage === undefined ? browserStorage() : storage;
    const raw = JSON.parse(store?.getItem(KEY) ?? "{}") as Partial<Prefs>;
    return {
      duplex: raw.duplex === true,
      ...(inRange(raw.studentCount, LIMITS.minStudents, LIMITS.maxStudents) ? { studentCount: raw.studentCount } : {}),
    };
  } catch {
    return { ...DEFAULT_PRINT };
  }
}

export function savePrefs(prefs: Prefs, storage?: Pick<Storage, "setItem"> | null) {
  try {
    const store = storage === undefined ? browserStorage() : storage;
    store?.setItem(KEY, JSON.stringify(prefs));
  } catch {
    /* storage unavailable: nothing to remember */
  }
}

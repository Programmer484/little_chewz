import { describe, expect, it } from "vitest";
import { loadPrefs, savePrefs } from "../src/lib/prefs.ts";

const memory = () => {
  const data = new Map<string, string>();
  return { getItem: (k: string) => data.get(k) ?? null, setItem: (k: string, v: string) => void data.set(k, v) };
};

describe("remembered settings", () => {
  it("round-trips class size and print options", () => {
    const store = memory();
    savePrefs({ order: "student", duplex: true, studentCount: 27, groupSize: 3 }, store);
    expect(loadPrefs(store)).toEqual({ order: "student", duplex: true, studentCount: 27, groupSize: 3 });
  });

  it("falls back to defaults for missing, bad or blocked storage", () => {
    expect(loadPrefs(memory())).toEqual({ order: "worksheet", duplex: false });
    const bad = memory();
    bad.setItem("little-chewz-print-pack:prefs", '{"studentCount": 9000, "order": "x"}');
    expect(loadPrefs(bad)).toEqual({ order: "worksheet", duplex: false });
    const blocked = { getItem: () => { throw new Error("blocked"); }, setItem: () => { throw new Error("blocked"); } };
    expect(loadPrefs(blocked)).toEqual({ order: "worksheet", duplex: false });
    expect(() => savePrefs({ order: "worksheet", duplex: false }, blocked)).not.toThrow();
    expect(loadPrefs(null)).toEqual({ order: "worksheet", duplex: false });
  });
});

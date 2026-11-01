/**
 * End-to-end: lessons from the Worker API, a teacher's selections, the plan,
 * resource fetches through the Worker, and browser-side assembly with pdf-lib.
 */
import { PDFDocument } from "pdf-lib";
import { describe, expect, it } from "vitest";
import { computePlan } from "../shared/plan.ts";
import type { LessonsResponse } from "../shared/types.ts";
import { PacketError } from "../src/lib/assemble.ts";
import { buildPacket } from "../src/lib/packet.ts";
import { handleRequest } from "../worker/index.ts";
import { env } from "./helpers.ts";

const demoEnv = env({ RESOURCE_MODE: "demo" });
/** The browser's fetch, routed straight into the Worker handler. */
const viaWorker = (async (input: RequestInfo | URL) =>
  handleRequest(new Request(new URL(String(input), "http://localhost:5173")), demoEnv)) as typeof fetch;

async function lessons(): Promise<LessonsResponse> {
  return (await (await viaWorker("/api/lessons")).json()) as LessonsResponse;
}

describe("print pack integration", () => {
  it("builds a real, openable demo packet with the expected pages", async () => {
    const lesson = (await lessons()).lessons.find((l) => l.lessonId === "demo-sample-lesson")!;
    const plan = computePlan(
      lesson,
      { choices: { station: "photo" }, extensions: { "photo-cards": true, "exit-ticket": true } },
      { studentCount: 25, groupSize: 4, adjusted: { "demo-exit-ticket": 3 } },
    );
    expect(plan.problems).toEqual([]);
    expect(plan.lines.map((l) => [l.resourceId, l.copies])).toEqual([
      ["demo-reading-log", 25], // 2 pages each
      ["demo-photo-prompt", 7], // 7 groups
      ["demo-team-cards", 2], // 7 cards at 4 per sheet
      ["demo-exit-ticket", 3],
    ]);
    expect(plan.totalPages).toBe(50 + 7 + 2 + 3);

    const stages = new Set<string>();
    const packet = await buildPacket(plan, (p) => stages.add(p.stage), viaWorker);
    expect(stages).toEqual(new Set(["fetching", "assembling"]));
    const doc = await PDFDocument.load(packet.bytes);
    expect(doc.getPageCount()).toBe(62);
    expect(packet.pageCount).toBe(62);
    const sizes = doc.getPages().map((p) => `${Math.round(p.getWidth())}x${Math.round(p.getHeight())}`);
    expect(sizes.slice(0, 50).every((s) => s === "612x792")).toBe(true);
    expect(sizes.slice(50, 57).every((s) => s === "792x612")).toBe(true); // landscape JPEG
    expect(sizes.slice(59)).toEqual(["595x842", "595x842", "595x842"]); // A4 exit ticket keeps its size
  });

  it("builds a Secret Ingredients packet from demo placeholders", async () => {
    const lesson = (await lessons()).lessons.find((l) => l.lessonId === "ccc-q01-secret-ingredients")!;
    expect(lesson.printable).toBe(true);
    const plan = computePlan(
      lesson,
      { choices: { "small-bite": "character-profile" }, extensions: { "character-profile-advanced": true } },
      { studentCount: 24, groupSize: 4 },
    );
    expect(plan.lines.map((l) => l.resourceId)).toEqual([
      "ccc-q01-secret-ingredients-clue-tracker-core",
      "ccc-q01-secret-ingredients-chapter-notes",
      "ccc-q01-secret-ingredients-character-profile-core",
      "ccc-q01-secret-ingredients-character-profile",
    ]);
    const packet = await buildPacket(plan, () => {}, viaWorker);
    expect((await PDFDocument.load(packet.bytes)).getPageCount()).toBe(96);
  });

  it("never returns a partial packet when one resource fails", async () => {
    const lesson = (await lessons()).lessons.find((l) => l.lessonId === "demo-sample-lesson")!;
    const plan = computePlan(lesson, { choices: { station: "poster" }, extensions: {} }, { studentCount: 5, groupSize: 4 });
    let calls = 0;
    const flaky = (async (input: RequestInfo | URL) => {
      calls++;
      if (String(input).includes("demo-station-poster")) return Response.json({ error: "Drive is down." }, { status: 502 });
      return viaWorker(input);
    }) as typeof fetch;
    await expect(buildPacket(plan, () => {}, flaky)).rejects.toThrow("Drive is down.");
    expect(calls).toBe(2);

    const html = (async () => new Response("<html>login</html>", { headers: { "content-type": "application/pdf" } })) as unknown as typeof fetch;
    await expect(buildPacket(plan, () => {}, html)).rejects.toThrow(PacketError);

    const offline = (async () => {
      throw new TypeError("network");
    }) as unknown as typeof fetch;
    await expect(buildPacket(plan, () => {}, offline)).rejects.toThrow(/Could not reach the server/);
  });

  it("refuses to build while the plan has problems", async () => {
    const lesson = (await lessons()).lessons.find((l) => l.lessonId === "demo-sample-lesson")!;
    const plan = computePlan(lesson, { choices: {}, extensions: {} }, { studentCount: 25, groupSize: 4 });
    await expect(buildPacket(plan, () => {}, viaWorker)).rejects.toThrow(/Choose one option/);
  });
});

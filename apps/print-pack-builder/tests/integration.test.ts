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
const PRINT = { duplex: false } as const;

async function lesson(id: string) {
  const data = (await (await viaWorker("/api/lessons")).json()) as LessonsResponse;
  return data.lessons.find((l) => l.lessonId === id)!;
}
const sizes = (doc: PDFDocument) => doc.getPages().map((p) => `${Math.round(p.getWidth())}x${Math.round(p.getHeight())}`);

describe("print pack integration", () => {
  const demoSelection = { choices: { station: "photo" }, extensions: { "photo-cards": true, "exit-ticket": true } };
  const demoNumbers = { studentCount: 25, groupSize: 4, copies: { "demo-exit-ticket:per_student": 3 } };

  it("builds a real, openable demo packet with the expected pages", async () => {
    const plan = computePlan(await lesson("demo-sample-lesson"), demoSelection, demoNumbers);
    expect(plan.problems).toEqual([]);
    expect(plan.lines.map((l) => [l.resourceId, l.copies])).toEqual([
      ["demo-reading-log", 25], // 2 pages each
      ["demo-photo-prompt", 7], // 7 groups
      ["demo-team-cards", 2], // 7 cards at 4 per sheet
      ["demo-exit-ticket", 3], // teacher typed 3
    ]);
    const stages = new Set<string>();
    const packet = await buildPacket(plan, PRINT, (p) => stages.add(p.stage), viaWorker);
    expect(stages).toEqual(new Set(["fetching", "assembling"]));
    const doc = await PDFDocument.load(packet.bytes);
    expect(doc.getPageCount()).toBe(62);
    const s = sizes(doc);
    expect(s.slice(0, 50).every((x) => x === "612x792")).toBe(true);
    expect(s.slice(50, 57).every((x) => x === "792x612")).toBe(true); // landscape JPEG
    expect(s.slice(59)).toEqual(["595x842", "595x842", "595x842"]); // A4 exit ticket keeps its size
  });

  it("builds student packets, double-sided", async () => {
    const plan = computePlan(await lesson("demo-sample-lesson"), demoSelection, demoNumbers);
    const packet = await buildPacket(plan, { duplex: true }, () => {}, viaWorker);
    // Packets: reading log (2 pages) + exit ticket (1 page + boundary blank) for students 1–3.
    // Then 7 photo prompts and 2 card sheets, each with a blank back.
    expect(packet.pageCount).toBe(3 * 4 + 22 * 2 + 7 * 2 + 2 * 2);
    expect(packet.sheetCount).toBe(packet.pageCount / 2);
    const s = sizes(await PDFDocument.load(packet.bytes));
    expect(s.slice(0, 4)).toEqual(["612x792", "612x792", "595x842", "595x842"]); // student 1: log, ticket, blank back
  });

  it("builds a Secret Ingredients packet from demo placeholders", async () => {
    const si = await lesson("ccc-q01-secret-ingredients");
    expect(si.printable).toBe(true);
    const plan = computePlan(
      si,
      { choices: { "step-4-choice": "step-4-b" }, extensions: { "step-4-b-more-ccc-q01-secret-ingredients-character-profile": true } },
      { studentCount: 24, groupSize: 4 },
    );
    expect(plan.lines.map((l) => l.resourceId)).toEqual([
      "ccc-q01-secret-ingredients-clue-tracker-core",
      "ccc-q01-secret-ingredients-chapter-notes",
      "ccc-q01-secret-ingredients-character-profile-core",
      "ccc-q01-secret-ingredients-character-profile",
    ]);
    const packet = await buildPacket(plan, PRINT, () => {}, viaWorker);
    expect((await PDFDocument.load(packet.bytes)).getPageCount()).toBe(96);
  });

  it("never returns a partial packet when one worksheet fails", async () => {
    const plan = computePlan(await lesson("demo-sample-lesson"), { choices: { station: "poster" }, extensions: {} }, { studentCount: 5, groupSize: 4 });
    let calls = 0;
    const flaky = (async (input: RequestInfo | URL) => {
      calls++;
      if (String(input).includes("demo-station-poster")) return Response.json({ error: "Drive is down." }, { status: 502 });
      return viaWorker(input);
    }) as typeof fetch;
    await expect(buildPacket(plan, PRINT, () => {}, flaky)).rejects.toThrow("Drive is down.");
    expect(calls).toBe(2);

    const html = (async () => new Response("<html>login</html>", { headers: { "content-type": "application/pdf" } })) as unknown as typeof fetch;
    await expect(buildPacket(plan, PRINT, () => {}, html)).rejects.toThrow(PacketError);

    const offline = (async () => {
      throw new TypeError("network");
    }) as unknown as typeof fetch;
    await expect(buildPacket(plan, PRINT, () => {}, offline)).rejects.toThrow(/Could not reach the server/);
  });

  it("refuses to build while the plan has problems", async () => {
    const plan = computePlan(await lesson("demo-sample-lesson"), { choices: {}, extensions: {} }, { studentCount: 25, groupSize: 4 });
    await expect(buildPacket(plan, PRINT, () => {}, viaWorker)).rejects.toThrow(/Choose one option/);
  });
});

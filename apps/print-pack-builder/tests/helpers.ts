import { PDFDocument } from "pdf-lib";
import { resolveLesson } from "../shared/manifest.ts";
import type { ClientResource, LessonManifest, ResolvedLesson } from "../shared/types.ts";
import { base64Decode } from "../worker/b64.ts";
import { FIXTURES } from "../worker/demo/fixtures.generated.ts";
import type { Env } from "../worker/env.ts";

export const fixture = (name: string) => base64Decode(FIXTURES[name]);

export async function pdfWithPages(n: number, size: [number, number] = [612, 792]): Promise<Uint8Array> {
  const doc = await PDFDocument.create();
  for (let i = 0; i < n; i++) doc.addPage(size).drawText(`Page ${i + 1}`, { x: 50, y: 50 });
  return doc.save();
}

/** A small hand-built lesson for plan tests. */
export const testManifest: LessonManifest = {
  lessonId: "test-lesson",
  questId: "q",
  order: 1,
  title: "Test Lesson",
  status: "ready",
  sections: [
    { kind: "core", id: "core", title: "Core", materials: [{ resourceId: "core-sheet", quantity: { rule: "per_student" }, pages: 2 }] },
    {
      kind: "choice",
      id: "bite",
      title: "Small Bite",
      options: [
        { id: "a", label: "A", title: "Song", materials: [{ resourceId: "song-sheet", quantity: { rule: "per_student" }, pages: 1 }] },
        {
          id: "b",
          label: "B",
          title: "Cards",
          materials: [{ resourceId: "team-cards", quantity: { rule: "per_group" }, cardsPerSheet: 4, pages: 1 }],
          extensions: [
            { id: "b-extra", title: "B extra", materials: [{ resourceId: "b-extra-sheet", quantity: { rule: "per_student" }, pages: 1 }] },
          ],
        },
        { id: "c", label: "C", title: "Talk", materials: [] },
      ],
    },
    {
      kind: "optional",
      id: "extras",
      title: "Extras",
      items: [
        { id: "poster", title: "Poster", materials: [{ resourceId: "poster", quantity: { rule: "per_class" }, pages: 1 }] },
        { id: "exit", title: "Exit", materials: [{ resourceId: "exit-ticket", quantity: { rule: "teacher_adjustable", count: 10 } }] },
        { id: "locked", title: "Locked", materials: [{ resourceId: "locked-sheet", quantity: { rule: "per_student" }, pages: 1 }] },
        { id: "reuse", title: "Reuse core", materials: [{ resourceId: "core-sheet", quantity: { rule: "per_group" }, pages: 2 }] },
      ],
    },
  ],
};

export function testLesson(): ResolvedLesson {
  return resolveLesson(testManifest, new Map([["q", { id: "q", title: "Quest", order: 1 }]]), (id): ClientResource =>
    id === "locked-sheet"
      ? { id, title: "Locked Sheet", available: false, reason: "Awaiting review for the pilot." }
      : { id, title: id, available: true },
  );
}

export function env(overrides: Partial<Env> = {}): Env {
  return {
    ASSETS: { fetch: async () => new Response("asset") } as unknown as Fetcher,
    RESOURCE_MODE: "disabled",
    ...overrides,
  };
}

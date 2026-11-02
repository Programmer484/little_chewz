import type { LessonsResponse } from "../../shared/types.ts";

export async function loadLessons(fetcher: typeof fetch = fetch): Promise<LessonsResponse> {
  const res = await fetcher("/api/lessons", { credentials: "same-origin" });
  if (!res.ok) throw new Error(`Could not load lessons (error ${res.status}).`);
  return (await res.json()) as LessonsResponse;
}

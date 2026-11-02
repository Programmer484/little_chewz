/**
 * Bundles the repository's own records into the Worker at build time:
 * the resource catalogue, the quest index, every quest.json and every
 * lesson.json. Nothing is copied or configured by hand; redeploy after
 * those files change.
 */
import registry from "../../../catalog/resources.json";
import questIndex from "../../../catalog/quests.json";
import demoLesson from "../config/demo/lesson.json";
import demoResources from "../config/demo/resources.json";
import type { LessonManifest } from "../shared/types.ts";
import { type DemoResource, type QuestIndex, type Registry, createCatalog } from "./catalog.ts";

const PREFIX = "../../../";
const questFiles = import.meta.glob("../../../content/*/*/quest.json", { eager: true, import: "default" });
const lessonFiles = import.meta.glob("../../../content/*/*/lessons/*/lesson.json", { eager: true, import: "default" });

/** Repository files keyed by repo-relative path, e.g. "content/.../quest.json". */
const files = Object.fromEntries(
  Object.entries({ ...questFiles, ...lessonFiles }).map(([path, value]) => [path.slice(PREFIX.length), value]),
);

const demoFiles = Object.fromEntries(Object.entries(demoResources).filter(([key]) => !key.startsWith("$")));

export const catalog = createCatalog({
  registry: registry as unknown as Registry,
  questIndex: questIndex as unknown as QuestIndex,
  files,
  demo: {
    lesson: demoLesson as LessonManifest,
    quest: { id: "demo", title: "Demo (synthetic files)", order: -1 },
    resources: demoFiles as Record<string, DemoResource>,
  },
});

/** Bundles the version-controlled configuration into the Worker at build time. */
import registry from "../../../catalog/resources.json";
import demoLesson from "../config/demo/lesson.json";
import demoResources from "../config/demo/resources.json";
import allowlist from "../config/pilot-allowlist.json";
import quests from "../config/quests.json";
import type { LessonManifest, PilotAllowEntry, QuestInfo } from "../shared/types.ts";
import { type DemoResource, type Registry, createCatalog } from "./catalog.ts";

// New lessons are added by dropping a manifest into config/lessons/.
const lessonModules = import.meta.glob<LessonManifest>("../config/lessons/*.json", { eager: true, import: "default" });

export const MANIFESTS: LessonManifest[] = Object.values(lessonModules);

const demoFiles = Object.fromEntries(Object.entries(demoResources).filter(([key]) => !key.startsWith("$")));

export const catalog = createCatalog({
  registry: registry as unknown as Registry,
  allowlist: allowlist.resources as Record<string, PilotAllowEntry>,
  manifests: MANIFESTS,
  quests: quests as QuestInfo[],
  demo: {
    lesson: demoLesson as LessonManifest,
    quest: { id: "demo", title: "Demo (synthetic files)", order: -1 },
    resources: demoFiles as Record<string, DemoResource>,
  },
});

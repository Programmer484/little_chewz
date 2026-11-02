import type { ResolvedLesson, ResourceMode } from "../../shared/types.ts";
import { navigate } from "../lib/route.ts";

export function lessonState(lesson: ResolvedLesson): { label: string; tone: "ready" | "none" | "waiting" } {
  if (lesson.status === "no_student_printing") return { label: "No student printing needed", tone: "none" };
  if (lesson.status === "in_progress") return { label: "Materials coming soon", tone: "waiting" };
  if (!lesson.printable) return { label: "Materials awaiting review", tone: "waiting" };
  return { label: "Build a print pack", tone: "ready" };
}

export function LessonList({ lessons, mode }: { lessons: ResolvedLesson[]; mode: ResourceMode }) {
  const quests = new Map<string, ResolvedLesson[]>();
  for (const l of lessons) quests.set(l.questTitle, [...(quests.get(l.questTitle) ?? []), l]);
  return (
    <>
      <section className="intro">
        <h1>Prepare your printing</h1>
        <p>Choose a lesson, pick your activities, enter your class size, and download one PDF with every worksheet you need.</p>
        {mode === "disabled" && (
          <p className="notice">Worksheet downloads are not switched on for this site yet. You can still explore the lessons.</p>
        )}
      </section>
      {[...quests.entries()].map(([quest, items]) => (
        <section key={quest} className="quest" aria-labelledby={`q-${items[0].questId}`}>
          <h2 id={`q-${items[0].questId}`}>{quest}</h2>
          <ul className="lesson-grid">
            {items.map((lesson) => {
              const state = lessonState(lesson);
              const href = `/lesson/${lesson.lessonId}`;
              return (
                <li key={lesson.lessonId}>
                  <a
                    className={`lesson-card tone-${state.tone}`}
                    href={href}
                    onClick={(e) => {
                      e.preventDefault();
                      navigate(href);
                    }}
                  >
                    <span className="lesson-title">{lesson.title}</span>
                    <span className="lesson-state">
                      {state.tone === "ready" ? "→ " : ""}
                      {state.label}
                    </span>
                  </a>
                </li>
              );
            })}
          </ul>
        </section>
      ))}
    </>
  );
}

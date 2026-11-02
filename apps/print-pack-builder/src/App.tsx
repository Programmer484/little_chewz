import { useEffect, useState } from "react";
import type { LessonsResponse } from "../shared/types.ts";
import { loadLessons } from "./lib/api.ts";
import { navigate, useRoute } from "./lib/route.ts";
import { LessonBuilder } from "./pages/LessonBuilder.tsx";
import { LessonList } from "./pages/LessonList.tsx";

export function App() {
  const route = useRoute();
  const [data, setData] = useState<LessonsResponse | null>(null);
  const [failure, setFailure] = useState<string | null>(null);

  useEffect(() => {
    loadLessons()
      .then(setData)
      .catch((e: Error) => setFailure(e.message));
  }, []);

  const lesson = route.page === "lesson" ? data?.lessons.find((l) => l.lessonId === route.lessonId) : undefined;

  return (
    <div className="shell">
      <header className="masthead">
        <a
          className="brand"
          href="/"
          onClick={(e) => {
            e.preventDefault();
            navigate("/");
          }}
        >
          <span className="brand-name">Little Chewz</span>
          <span className="brand-tool">Print Pack Builder</span>
        </a>
        {data?.mode === "demo" && <span className="badge">Demo mode · sample files only</span>}
      </header>
      <main id="main">
        {failure && (
          <p className="alert" role="alert">
            {failure}
          </p>
        )}
        {!data && !failure && <p className="muted">Loading lessons…</p>}
        {data && route.page === "home" && <LessonList lessons={data.lessons} mode={data.mode} />}
        {data && route.page === "lesson" && lesson && <LessonBuilder key={lesson.lessonId} lesson={lesson} />}
        {data && route.page === "lesson" && !lesson && (
          <section className="panel">
            <h1>Lesson not found</h1>
            <p>This lesson is not in the Print Pack Builder.</p>
            <button className="button" onClick={() => navigate("/")}>
              See all lessons
            </button>
          </section>
        )}
      </main>
      <footer className="footer">Little Chewz · Chewlandia Academy</footer>
    </div>
  );
}

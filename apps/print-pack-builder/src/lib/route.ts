import { useEffect, useState } from "react";

/** Minimal routing: "/" lists lessons, "/lesson/<lessonId>" opens one lesson's builder. */
export type Route = { page: "home" } | { page: "lesson"; lessonId: string };

export function parseRoute(pathname: string): Route {
  const m = /^\/lesson\/([a-z0-9-]+)\/?$/.exec(pathname);
  return m ? { page: "lesson", lessonId: m[1] } : { page: "home" };
}

export function navigate(path: string) {
  window.history.pushState(null, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
  window.scrollTo(0, 0);
}

export function useRoute(): Route {
  const [route, setRoute] = useState(() => parseRoute(window.location.pathname));
  useEffect(() => {
    const update = () => setRoute(parseRoute(window.location.pathname));
    window.addEventListener("popstate", update);
    return () => window.removeEventListener("popstate", update);
  }, []);
  return route;
}

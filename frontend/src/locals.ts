import { defineMiddleware } from "astro:middleware";
import { AstroError } from "astro/errors";

import type { CoursePage, RouteData } from "./lib/route-data";

/**
 * Middleware to provide context about the current page.
 */
export const onRequest = defineMiddleware((context, next) => {
  context.locals.ohmRoute = { breadcrumbs: [] };
  initializeOhmCourse(context.locals);
  return next();
});

/** Prepares context data for a course page, which is used to render it. */
function initializeOhmCourse(locals: App.Locals) {
  let course: CoursePage | undefined;

  Object.defineProperty(locals, "ohmCourse", {
    get() {
      if (!course) {
        throw new AstroError(
          "`locals.ohmCourse` is not set.",
          "A component that reads `locals.ohmCourse` was rendered outside of an edition, chapter or section route.",
        );
      }
      return course;
    },
    set(value: CoursePage) {
      course = value;
    },
  });
}

export function setRouteData(locals: App.Locals, { route, course }: RouteData) {
  locals.ohmRoute = route;
  if (course) {
    locals.ohmCourse = course;
  }
}

---
name: TypeScript Guidelines
description: "Use when creating or changing TypeScript, browser-side recipe interactions, HTMX handlers, or compiled JavaScript in this Django application."
applyTo: "src/**/*.ts"
---

# TypeScript guidelines

- Keep modules focused on one responsibility and prefer small, typed functions over growing a single manager or event handler.
- Follow the strict compiler settings in [`tsconfig.json`](../../tsconfig.json). Give domain values useful types, narrow nullable DOM results before use, and avoid introducing `any`.
- Preserve the current browser architecture: TypeScript modules in `src/` compile as ES modules into `static/js/`; Django templates load those compiled modules. Make source changes in `src/`, not by hand in generated JavaScript or source maps.
- Use `textContent` for user-controlled text. Do not interpolate dynamic values into `innerHTML`; if markup is necessary, construct elements and set attributes explicitly.
- Add unit tests for non-trivial behavior and regressions. The repository currently has no TypeScript test runner, and `tsconfig.json` excludes `*.spec.ts`; any new tests must be runnable and included in a test/type-check configuration rather than being inert files.
- Run `npm run build` after TypeScript changes and inspect the generated-output diff. `package.json` currently has no test script.
- Add inline comments only when they explain a non-obvious state transition, browser/API constraint, or invariant.

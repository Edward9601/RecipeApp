# Agent guidance

Read the [repository map](docs/repo-map.md) before broad changes. It describes the current architecture and request flows. Consult the [development guide](docs/development.md) for commands, runtime versions, and configuration notes, and check [known issues](docs/known-issues.md) before changing an affected area.

- Keep each module and function focused on one responsibility. Keep HTTP handling, validation, persistence, and browser behavior separated.
- For new non-trivial Django persistence logic, use an app-local repository layer and keep views/forms from accumulating query and persistence workflows. Avoid one-method repository wrappers and do not refactor legacy code outside the task.
- Add focused unit tests for changed behavior and regression cases. Do not treat the currently sparse test suite as evidence that an area is covered.
- When a code change introduces non-obvious intent, invariants, or decisions, add a nearby inline comment explaining why; do not narrate straightforward code.
- Follow the TypeScript and Django rules in [`.github/instructions/typescript.instructions.md`](.github/instructions/typescript.instructions.md) and [`.github/instructions/django.instructions.md`](.github/instructions/django.instructions.md) for matching files.
- Treat `src/**/*.ts` as the frontend source of truth. Regenerate `static/js/` with the documented build command rather than editing compiled output by hand.
- Preserve existing behavior unless a task explicitly calls for a behavior change. Make changes surgical, report discovered adjacent risks, and do not silently broaden scope.
- Use `requirements.txt` and `package-lock.json` as dependency-version references. Do not add or upgrade dependencies without a task need.

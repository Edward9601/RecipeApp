---
name: Django Guidelines
description: "Use when creating or changing Python, Django models, forms, views, repositories, migrations, authentication, or Django tests in this application."
applyTo: "**/*.py"
---

# Django guidelines

- Give each module and function one clear responsibility. Keep views focused on HTTP flow and response handling; keep form validation in forms and multi-step persistence workflows out of views.
- There is no established repository layer yet. For new non-trivial data-access logic, use an app-local repository module (for example, `recipes/repositories/`) and call it from the appropriate application layer. Do not add a repository wrapper for a single obvious ORM operation, and do not create a broad abstraction solely to retrofit existing code.
- Preserve the current domain model: regular recipes and sub-recipes are `Recipe` rows distinguished by `is_sub_recipe`, with their relationship represented by `RecipeSubRecipe`. Do not reintroduce the old separate sub-recipe model.
- Enforce object ownership and object type at the query/view boundary for every mutating endpoint. Never rely only on a hidden button or template check for authorization.
- Use transactions for coordinated writes to a recipe and its related records. Keep cache invalidation aligned with committed database changes.
- Add Django `TestCase` coverage for validation, permissions, persistence, and regression cases. Place recipe tests under `recipes/tests/`; verify that the tests actually run with `python manage.py test`.
- Treat migrations as persistent deployment history. Generate and review schema changes with Django migration commands; do not edit an old migration or delete/squash history as an incidental cleanup.
- Avoid broad exception catches and success-shaped fallbacks. Preserve useful HTTP status codes and validation details, and log unexpected failures through the project's logging conventions rather than `print`.
- Add inline comments only when they explain a non-obvious invariant, migration/data-safety constraint, or design decision.
- Check [known issues](../../docs/known-issues.md) when working around settings, cache behavior, recipe ownership, image storage, or sub-recipe relations; document any intentional behavior change.

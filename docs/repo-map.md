# RecipeApp repository map

## What this application is

RecipeApp is a server-rendered Django site, not a single-page application. Django templates produce the recipe, sub-recipe, and account pages. Bootstrap supplies the UI components; HTMX fetches modal fragments and recipe search results; TypeScript manages browser interactions and compiles to JavaScript modules served as static files.

The Python dependency versions are pinned in [`requirements.txt`](../requirements.txt); Django is 6.1.3. Python 3.14 is the only supported and tested runtime, selected for Render by [`.python-version`](../.python-version) and for CI by [`.github/workflows/django.yml`](../.github/workflows/django.yml). The frontend declares TypeScript `^5.8.3` in [`package.json`](../package.json), with 5.8.3 currently locked in [`package-lock.json`](../package-lock.json). The project does not declare its own Node runtime version.

## Runtime and request flow

- [`manage.py`](../manage.py) loads [`mywebsite.settings`](../mywebsite/settings.py).
- [`mywebsite/urls.py`](../mywebsite/urls.py) mounts user/account URLs and Django auth URLs at the site root, then mounts recipe URLs under `/recipes/`.
- [`users/`](../users/) implements registration, login, logout, and guest login using Django's built-in `User`.
- [`recipes/urls.py`](../recipes/urls.py) routes recipe and sub-recipe list/detail/create/update/delete requests and the ingredient/step modal endpoints to the class-based views in [`recipes/views/`](../recipes/views/).
- Recipe list filtering uses [`RecipeFilterForm`](../recipes/forms/recipe_filter_forms.py). Recipe and sub-recipe search requests are detected through HTMX and return list partials.
- Ingredient and step modals are fetched as Django template fragments. Their POST endpoints validate inline formsets, persist the related rows, and return JSON for the browser to apply to the detail page.
- Recipe create/update forms live in [`recipes/forms/recipe_forms.py`](../recipes/forms/recipe_forms.py). Shared recipe formset/cache helpers are in [`recipes/handlers/recipes_handler.py`](../recipes/handlers/recipes_handler.py).
- There is no dedicated repository layer today; ORM access currently appears in views, forms, and the recipe handler. The repository-pattern guidance applies to new, non-trivial persistence logic rather than an unrelated legacy refactor.

## Domain model

The current schema is defined in [`recipes/models/`](../recipes/models/):

- `Recipe` is the central entity for both ordinary recipes and sub-recipes. `is_sub_recipe` distinguishes the two kinds; there is no separate current `SubRecipe` model.
- `RecipeIngredient` and `RecipeStep` are related to a recipe and store ingredient details and ordered instructions.
- `Category` and `Tag` are many-to-many metadata on recipes.
- `RecipeSubRecipe` is the explicit through model for parent/sub-recipe relationships.
- `RecipeImage` associates uploaded images with a recipe.

The schema history is in [`recipes/migrations/`](../recipes/migrations/). The migration chain ends at `0046`; migration `0046` removes the former standalone sub-recipe models. Treat migrations as deployment history and inspect them before changing the current model structure.

## Frontend source and templates

- TypeScript source is under [`src/`](../src/). [`src/recipes/main.ts`](../src/recipes/main.ts) initializes filtering, recipe forms, and HTMX-loaded ingredient/step modals.
- Recipe form and modal logic is split between [`src/recipes/`](../src/recipes/) and the shared unsaved-changes manager in [`src/shared/`](../src/shared/).
- [`tsconfig.json`](../tsconfig.json) enables strict checking and emits ES6 modules into [`static/js/`](../static/js/). Django templates load these compiled modules. Edit TypeScript source, then rebuild; do not hand-edit compiled output.
- Page templates are in [`recipes/templates/`](../recipes/templates/), account templates in [`users/templates/`](../users/templates/), and the shared site shell in [`templates/`](../templates/).
- Application styles are split between [`recipes/static/recipes/css/`](../recipes/static/recipes/css/) and [`static/css/`](../static/css/); both are referenced by shared templates.

## Configuration, storage, and deployment

- [`mywebsite/settings.py`](../mywebsite/settings.py) configures installed apps, database selection, Redis cache/session storage, static/media storage, authentication redirects, and S3 storage.
- [`render.yaml`](../render.yaml) describes the Render web service. [`README.md`](../README.md) contains the original local setup and deployment walkthrough.
- Environment-variable behavior is not conventional: `DJANGO_ENV` controls whether `.env` is loaded, while `ENVIRONMENT` selects database/cache branches. See the [development guide](development.md) and [known issues](known-issues.md) before changing these settings.
- [`utils/models.py`](../utils/models.py) contains image storage, conversion, orientation, and thumbnail helpers. [`utils/helpers/`](../utils/helpers/) contains the registered-user mixin and guest-name constant.
- [`recipes/management/commands/populate_categories.py`](../recipes/management/commands/populate_categories.py) seeds preset categories and tags; review its data effects before running it.

## Tests and checks

- Django tests are located under [`recipes/tests/`](../recipes/tests/) plus app-level `tests.py` modules in `users/` and `utils/`.
- The GitHub Actions workflow runs migrations and `python manage.py test`.
- The frontend currently has a TypeScript build but no configured test runner. The TypeScript compiler excludes `*.spec.ts`.
- The current test suite is sparse; see [known issues](known-issues.md) rather than assuming a module is covered because a test file exists.

For runnable commands, the environment-variable mapping, and current validation limits, see the [development guide](development.md).

# Milestone 1 Frontend Foundation

## Delivered

- React 19 application built with Vite.
- BrowserRouter entry point and top-level public, login, system-access, and dashboard route structure.
- Shared layout and API client with normalized JSON/error handling.
- Homepage health request displaying connected or unavailable state.
- Explicit unavailable states for regular and separate system-access login pages.
- Protective redirect of all dashboard paths to regular login while authentication was deferred.
- Placeholder public content and dashboard pages matching the final project layout.

## Tests and build boundary

The initial frontend tests covered successful and failed backend health calls, both login placeholders, dashboard redirects, API URL normalization, JSON request headers, and error normalization.

At the Milestone 2 baseline check, the unchanged Milestone 1 frontend suite reported:

```text
2 test files passed
10 tests passed
```

The production-build command was established as `docker compose exec frontend npm run build`.

## Commit

`0899153 feat(frontend): scaffold React application shell`

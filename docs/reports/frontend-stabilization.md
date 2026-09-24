# Frontend stabilization acceptance — 2026-09-10

Status: browser confirmation received; automated Chromium and Firefox acceptance passed on 2026-09-24.

## Runtime restoration

Restored `frontend/package.json` to the tracked development command, `vite --host 0.0.0.0`, removing the uncommitted `NODE_ENV=production` / `--mode production` workaround. Restarted the Compose frontend and confirmed Vite starts in normal development mode. This restoration produces no package diff against HEAD. No application behavior, API, dependency, or schema change was made; no speculative regression test was added without a reproducible failure.

## Acceptance evidence

All checks below were run after restoration against the local Compose runtime.

| Check | Actual result |
| --- | --- |
| `docker compose exec frontend npm test` | 72 tests passed in 16 files on 2026-09-24 |
| `docker compose exec backend pytest -q backend/tests` | 138 tests passed on 2026-09-24 |
| `docker compose exec frontend npm run build` | Passed; 98 modules transformed on 2026-09-24 |
| `docker compose -p cms-e2e -f compose.yaml -f compose.e2e.yaml run --build --rm e2e` | 10 tests passed: five journeys in Chromium and Firefox on 2026-09-24 |
| HTTP GET `/src/pages/public/PageView.jsx` | 200 OK, `Content-Type: text/javascript`, no redirect |
| Fresh headless Firefox, `/` | Rendered site chrome and final empty article/announcement states after API completion |
| Fresh Firefox, `/login` and `/system-access` | Rendered both distinct login forms |
| Fresh Firefox, `/announcements` | Rendered final empty state |
| Fresh Firefox, `/articles/missing-stabilization-check` | Rendered “Story not found” after API 404 |
| Fresh Firefox, `/pages/missing-stabilization-check` | Rendered “Page not found” after API 404 |
| Firefox WebDriver BiDi network/log capture on all six routes | No fetch errors, failed application-module responses, or error-level browser log events; favicon 404 and intentional missing-content API 404s were observed |

The browser probe used a separate temporary Firefox profile and waited for body content with loading states resolved. Local diagnostic artifacts are `/tmp/cms-stabilization-browser.mjs`, `/tmp/cms-stabilization-browser.json`, `/tmp/cms-stabilization-headers`, and `/tmp/cms-stabilization-pageview.js`; these are temporary evidence, not committed artifacts or a regression suite.

## Original-browser confirmation

On 2026-09-11, the reporter confirmed that the CMS now renders correctly in the
originally affected browser. Since the failure no longer reproduces and no
application behavior change was made, there is no failure signature to turn into
a targeted regression test.

## Automated browser acceptance

The disposable Compose suite provisions test-only Publisher, Admin, and Superadmin accounts. It checks public startup and both login flows; an article with a real uploaded picture through submission, approval, publication, and unpublication; and a published page on direct navigation. It also checks category, tag, media link, image upload, and Publisher-account management, plus role boundaries and public display of saved site settings. All five journeys passed in Chromium and Firefox.

An early run exposed a corrupt PNG fixture: Pillow raised `SyntaxError`, and upload returned 500. The storage adapter now maps that decoder error to the existing invalid-media response, with a backend regression test. Selector ambiguity in the expanded browser checks was fixed in the tests. The final suite passed with no failures.

The pre-existing deletion of `docs/reports/architecture-audit.md` and untracked `docs/reports/milestone-6/` files were preserved and excluded from this documentation commit.

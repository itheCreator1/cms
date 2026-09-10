# Frontend stabilization acceptance — 2026-09-10

Status: incomplete. The reported affected-browser blank screen has not been reproduced or diagnosed. Milestone 6 remains gated on that verification.

## Runtime restoration

Restored `frontend/package.json` to the tracked development command, `vite --host 0.0.0.0`, removing the uncommitted `NODE_ENV=production` / `--mode production` workaround. Restarted the Compose frontend and confirmed Vite starts in normal development mode. This restoration produces no package diff against HEAD. No application behavior, API, dependency, or schema change was made; no speculative regression test was added without a reproducible failure.

## Acceptance evidence

All checks below were run after restoration against the local Compose runtime.

| Check | Actual result |
| --- | --- |
| `docker compose exec frontend npm test` | 42 tests passed in 9 files |
| `docker compose exec backend pytest -q backend/tests` | 119 tests passed |
| `docker compose exec frontend npm run build` | Passed; 79 modules transformed |
| HTTP GET `/src/pages/public/PageView.jsx` | 200 OK, `Content-Type: text/javascript`, no redirect |
| Fresh headless Firefox, `/` | Rendered site chrome and final empty article/announcement states after API completion |
| Fresh Firefox, `/login` and `/system-access` | Rendered both distinct login forms |
| Fresh Firefox, `/announcements` | Rendered final empty state |
| Fresh Firefox, `/articles/missing-stabilization-check` | Rendered “Story not found” after API 404 |
| Fresh Firefox, `/pages/missing-stabilization-check` | Rendered “Page not found” after API 404 |
| Firefox WebDriver BiDi network/log capture on all six routes | No fetch errors, failed application-module responses, or error-level browser log events; favicon 404 and intentional missing-content API 404s were observed |

The browser probe used a separate temporary Firefox profile and waited for body content with loading states resolved. Local diagnostic artifacts are `/tmp/cms-stabilization-browser.mjs`, `/tmp/cms-stabilization-browser.json`, `/tmp/cms-stabilization-headers`, and `/tmp/cms-stabilization-pageview.js`; these are temporary evidence, not committed artifacts or a regression suite.

## Remaining evidence

The available tools do not expose the affected browser’s Network panel. Its browser identity, failed request status/response/redirects/blocking reason, and console startup error were requested from the user. The reported `file:///` message has not been connected to the module request by evidence.

Fresh-profile success does not establish affected-profile success. Published article/page success was not exercised in this live browser run; the homepage returned no published articles. Existing frontend tests cover populated article and page rendering with mocked API responses. Complete the original-browser investigation and published-detail acceptance before claiming stabilization or beginning Milestone 6.

The pre-existing deletion of `docs/reports/architecture-audit.md` and untracked `docs/reports/milestone-6/` files were preserved and excluded from this documentation commit.

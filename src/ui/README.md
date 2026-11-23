# cigarlog UI

React 19 + TypeScript SPA built with Vite. First milestone: OIDC login and profile settings.

## Env vars

| Variable | Default | Purpose |
|---|---|---|
| `VITE_OIDC_AUTHORITY` | `http://localhost:8080/local` | OIDC issuer URL (mock-oauth2-server in dev) |
| `VITE_OIDC_CLIENT_ID` | `cigarlog` | OAuth client ID |
| `VITE_API_BASE_URL` | `http://localhost:8000` | FastAPI base URL |

## Commands

```bash
npm run dev          # dev server on :5173
npm run build        # production build
npm test             # unit tests (Vitest + MSW)
npx playwright test  # e2e tests (requires running stack)
```

## Auth flow

1. User clicks **Sign in** → `userManager.signinRedirect()` → redirected to OIDC provider
2. Provider redirects back to `/callback`
3. `Callback.tsx` calls `signinRedirectCallback()`, stores token in memory, navigates to `/settings`
4. All API calls inject `Authorization: Bearer {token}` via `fetchWithAuth`
5. Tokens are held in memory only — never in localStorage

## Project structure

```
src/
  auth/         OIDC config, AuthProvider context, RequireAuth guard, Callback handler
  api/          fetch wrapper + typed /v1/me client
  routes/       login, callback, settings pages
  components/   shared UI primitives (Button, Input, Label, FormField)
  styles/       Tailwind globals
  tests/        Vitest unit tests + MSW mocks + Playwright e2e stubs
```

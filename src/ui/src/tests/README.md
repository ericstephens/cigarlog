# UI Tests

## Unit / component tests (Vitest + RTL + MSW)

MSW intercepts all `/v1/*` API calls — no real API server needed.

```bash
cd src/ui
npm test          # single run
npm run test:watch  # watch mode
```

## E2E tests (Playwright)

Requires the full stack (`podman-compose up` from the repo root):

```bash
cd src/ui
npx playwright test
```

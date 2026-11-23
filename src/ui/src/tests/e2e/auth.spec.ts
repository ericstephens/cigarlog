import { test } from '@playwright/test'

test.describe('auth flow', () => {
  test.todo('redirects unauthenticated user to login')
  test.todo('completes OIDC callback and lands on settings')
  test.todo('profile update persists display name change')
})

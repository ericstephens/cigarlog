import type { UserManagerSettings } from 'oidc-client-ts'

export const oidcConfig: UserManagerSettings = {
  authority: import.meta.env.VITE_OIDC_AUTHORITY ?? 'http://localhost:8080/local',
  client_id: import.meta.env.VITE_OIDC_CLIENT_ID ?? 'cigarlog',
  redirect_uri: `${window.location.origin}/callback`,
  response_type: 'code',
  scope: 'openid email profile',
  post_logout_redirect_uri: window.location.origin,
  // Disable all automatic background behavior
  automaticSilentRenew: false,
  monitorSession: false,
  checkSessionIntervalInSeconds: 0,
}

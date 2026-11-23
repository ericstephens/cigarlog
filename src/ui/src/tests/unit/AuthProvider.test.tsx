import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { AuthProvider, useAuth } from '../../auth/AuthProvider'

vi.mock('oidc-client-ts', () => ({
  UserManager: vi.fn().mockImplementation(() => ({
    getUser: vi.fn().mockResolvedValue(null),
    signinRedirect: vi.fn(),
    signoutRedirect: vi.fn(),
    events: {
      addUserLoaded: vi.fn(),
      addUserUnloaded: vi.fn(),
      removeUserLoaded: vi.fn(),
    },
  })),
}))

function ShowAuth() {
  const { isAuthenticated } = useAuth()
  return <div>{isAuthenticated ? 'authenticated' : 'not-authenticated'}</div>
}

describe('AuthProvider', () => {
  it('reports not authenticated when no user', async () => {
    render(
      <AuthProvider>
        <ShowAuth />
      </AuthProvider>,
    )
    expect(await screen.findByText('not-authenticated')).toBeInTheDocument()
  })

  it('exposes login() that calls signinRedirect', async () => {
    const { UserManager } = await import('oidc-client-ts')
    const mockSignin = vi.fn()
    vi.mocked(UserManager).mockImplementation(() => ({
      getUser: vi.fn().mockResolvedValue(null),
      signinRedirect: mockSignin,
      signoutRedirect: vi.fn(),
      events: {
        addUserLoaded: vi.fn(),
        addUserUnloaded: vi.fn(),
        removeUserLoaded: vi.fn(),
      },
    } as never))

    function TriggerLogin() {
      const { login } = useAuth()
      return <button onClick={() => void login()}>login</button>
    }
    const { getByRole } = render(
      <AuthProvider>
        <TriggerLogin />
      </AuthProvider>,
    )
    getByRole('button').click()
    expect(mockSignin).toHaveBeenCalled()
  })
})

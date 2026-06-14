type TokenGetter = () => string | null | undefined

let authTokenGetter: TokenGetter = () => null

/** Registered by AuthContext when Stytch session is active. */
export function setAuthTokenGetter(getter: TokenGetter): void {
  authTokenGetter = getter
}

async function api(path: string, options: RequestInit = {}): Promise<Response> {
  const headers = new Headers(options.headers)
  const token = authTokenGetter()
  if (token) {
    headers.set("Authorization", `Bearer ${token}`)
  }
  // Include Stytch session cookies when SDK uses opaque/HttpOnly tokens (getTokens() null).
  return fetch(path, { ...options, headers, credentials: "include" })
}

export default api

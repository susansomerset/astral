import { getHadSession, setLogOffReason } from "./sessionAuthMark"

type TokenGetter = () => string | null | undefined

let authTokenGetter: TokenGetter = () => null

/** Registered by AuthContext when Stytch session is active. */
export function setAuthTokenGetter(getter: TokenGetter): void {
  authTokenGetter = getter
}

type UnauthorizedHandler = () => void
let unauthorizedHandler: UnauthorizedHandler | null = null

/** Registered by AuthContext — triggers re-render when api() sees 401. */
export function setUnauthorizedHandler(handler: UnauthorizedHandler | null): void {
  unauthorizedHandler = handler
}

async function api(path: string, options: RequestInit = {}): Promise<Response> {
  const headers = new Headers(options.headers)
  const token = authTokenGetter()
  if (token) {
    headers.set("Authorization", `Bearer ${token}`)
  }
  const response = await fetch(path, { ...options, headers, credentials: "include" })
  if (response.status === 401 && getHadSession()) {
    setLogOffReason("server-rejection")
    unauthorizedHandler?.()
  }
  return response
}

export default api

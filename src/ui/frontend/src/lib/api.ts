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

export const SILENT_AUTH_HEADER = "X-Astral-Silent-Auth"

/** `silent: true` — background poll; backend skips Stytch GetUser. Default verifies. */
export type ApiOptions = RequestInit & { silent?: boolean }

async function api(path: string, options: ApiOptions = {}): Promise<Response> {
  const { silent, headers: headerInit, ...rest } = options
  const headers = new Headers(headerInit)
  const token = authTokenGetter()
  if (token) {
    headers.set("Authorization", `Bearer ${token}`)
  }
  if (silent) {
    headers.set(SILENT_AUTH_HEADER, "1")
  }
  const response = await fetch(path, { ...rest, headers, credentials: "include" })
  if (response.status === 401 && getHadSession()) {
    setLogOffReason("server-rejection")
    unauthorizedHandler?.()
  }
  return response
}

export default api

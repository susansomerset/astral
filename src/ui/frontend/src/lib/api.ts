// TODO: replace with Auth0 access token once tenant is set up
const AUTH_TOKEN = "stub-susan-token"

async function api(path: string, options: RequestInit = {}): Promise<Response> {
  const headers = new Headers(options.headers)
  headers.set("Authorization", `Bearer ${AUTH_TOKEN}`)
  return fetch(path, { ...options, headers })
}

export default api

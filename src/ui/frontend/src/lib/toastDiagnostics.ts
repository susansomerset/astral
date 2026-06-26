export const ERROR_TOAST_DURATION_MS = 15000

export interface ToastDiagnostics {
  timestamp?: string
  route?: string
  astral_candidate_id?: string | null
  api_path?: string
  http_method?: string
  http_status?: number
  response_body?: string
  exception_type?: string
  traceback?: string
}

export interface ToastMessage {
  text: string
  variant?: "success" | "error" | "info"
  durationMs?: number
  diagnostics?: ToastDiagnostics
}

export class ApiError extends Error {
  readonly diagnostics: ToastDiagnostics
  constructor(message: string, diagnostics: ToastDiagnostics) {
    super(message)
    this.name = "ApiError"
    this.diagnostics = diagnostics
  }
}

/** Parse non-OK Response body; throw ApiError with enrichment fields when present. */
export async function readApiError(response: Response, apiPath: string, method = "GET"): Promise<never> {
  const body = await response.json().catch(() => ({} as Record<string, unknown>))
  const message =
    (typeof body.error === "string" && body.error) ||
    (typeof body.message === "string" && body.message) ||
    `HTTP ${response.status}`
  throw new ApiError(message, {
    timestamp: new Date().toISOString(),
    api_path: apiPath,
    http_method: method,
    http_status: response.status,
    response_body: JSON.stringify(body, null, 2),
    exception_type: typeof body.exception_type === "string" ? body.exception_type : undefined,
    traceback: typeof body.traceback === "string" ? body.traceback : undefined,
  })
}

export function errorToastFromApiError(err: ApiError): ToastMessage {
  return { text: err.message, variant: "error", diagnostics: err.diagnostics }
}

/** Multi-line clipboard bundle — stable key order for Linear paste. */
export function formatDiagnosticBundle(
  message: ToastMessage,
  route: string,
  candidateId: string | null,
): string {
  const d = message.diagnostics ?? {}
  const lines: string[] = [
    "Astral error diagnostic",
    `timestamp: ${d.timestamp ?? new Date().toISOString()}`,
    `message: ${message.text}`,
    `route: ${d.route ?? route}`,
  ]
  if (candidateId) lines.push(`astral_candidate_id: ${candidateId}`)
  if (d.api_path) lines.push(`api_path: ${d.api_path}`)
  if (d.http_method) lines.push(`http_method: ${d.http_method}`)
  if (d.http_status != null) lines.push(`http_status: ${d.http_status}`)
  if (d.exception_type) lines.push(`exception_type: ${d.exception_type}`)
  if (d.response_body) {
    lines.push("response_body:")
    lines.push(d.response_body)
  }
  if (d.traceback) {
    lines.push("traceback:")
    lines.push(d.traceback)
  }
  return lines.join("\n")
}

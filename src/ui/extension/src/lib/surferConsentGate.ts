/** Surfer consent pre-capture gate (AST-1238). Wire from AST-1170 background. */

export type SurferConsentDto = {
  is_current: boolean
  capture_denied_message: string
  status?: string
  [key: string]: unknown
}

export function mayCapture(dto: SurferConsentDto): boolean {
  return dto.is_current === true
}

export async function fetchConsent(
  apiBase: string,
  candidateId: string,
  authHeader: string,
): Promise<SurferConsentDto> {
  const r = await fetch(`${apiBase}/api/candidates/${candidateId}/surfer/consent`, {
    method: "GET",
    headers: { Authorization: `Bearer ${authHeader}` },
    credentials: "omit",
  })
  if (!r.ok) {
    throw new Error(`Surfer consent GET failed: HTTP ${r.status}`)
  }
  return (await r.json()) as SurferConsentDto
}

export async function assertMayCapture(
  apiBase: string,
  candidateId: string,
  authHeader: string,
): Promise<SurferConsentDto> {
  const dto = await fetchConsent(apiBase, candidateId, authHeader)
  if (!mayCapture(dto)) {
    throw new Error(dto.capture_denied_message)
  }
  return dto
}

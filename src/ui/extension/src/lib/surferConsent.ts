/** Surfer consent — server DTO + helpers (AST-1237). Shell/gate wire these (AST-1170 / AST-1238). */

export type SurferConsentDto = {
  status: string
  accepted_version: string | null
  updated_at: string | null
  current_version: string
  disclosure_copy: string
  is_current: boolean
  disclosure_title: string
  opt_in_label: string
  decline_label: string
  current_ok_title: string
  current_ok_body: string
}

/** True when capture must not proceed until she affirms the current wording. */
export function needsDisclosure(dto: SurferConsentDto): boolean {
  return dto.is_current !== true
}

/**
 * GET /api/candidates/<id>/surfer/consent via caller-supplied authenticated fetch.
 * Background context owns network I/O (AST-1170) — this module does not hardcode base URL or credentials.
 */
export async function fetchSurferConsent(
  candidateId: string,
  getJson: (path: string) => Promise<SurferConsentDto>,
): Promise<SurferConsentDto> {
  return getJson(`/api/candidates/${encodeURIComponent(candidateId)}/surfer/consent`)
}

/**
 * PUT opt_in with the DTO's current_version (the wording she was shown).
 * Does not accept a free-form version from the UI — always send dto.current_version.
 */
export async function optInSurferConsent(
  candidateId: string,
  dto: SurferConsentDto,
  putJson: (path: string, body: unknown) => Promise<SurferConsentDto>,
): Promise<SurferConsentDto> {
  return putJson(`/api/candidates/${encodeURIComponent(candidateId)}/surfer/consent`, {
    action: "opt_in",
    accepted_version: dto.current_version,
  })
}

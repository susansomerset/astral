/** Surfer opt-out helper for extension UI (AST-1238). Wire from AST-1170 popup. */

import type { SurferConsentDto } from "./surferConsentGate"

export async function optOutSurfer(
  apiBase: string,
  candidateId: string,
  authHeader: string,
): Promise<SurferConsentDto> {
  const r = await fetch(`${apiBase}/api/candidates/${candidateId}/surfer/consent`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${authHeader}`,
      "Content-Type": "application/json",
    },
    credentials: "omit",
    body: JSON.stringify({ action: "opt_out" }),
  })
  if (!r.ok) {
    throw new Error(`Surfer consent opt-out failed: HTTP ${r.status}`)
  }
  return (await r.json()) as SurferConsentDto
}
